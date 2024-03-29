from __future__ import print_function, unicode_literals

import time
import random
import multiprocessing

from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.nltk import default_message_generator

import logging
logger = logging.getLogger(__name__)

_generator = default_message_generator()

def script_setup(context):
	use_threads = context.as_bool('use_threads', False)
	if use_threads:
		_lock = multiprocessing.Lock()
		_list_1 = list()
		_list_2 = list()
	else:
		logging.warn("Creating a new  multiprocessing Manager")
		manager = multiprocessing.Manager()
		_lock = manager.Lock()
		_list_1 = manager.list()
		_list_2 = manager.list()
	
	context['list.lock'] = _lock
	context['created_notes'] = _list_1
	context['updated_notes'] = _list_2
	
def script_teardown(context):
	del context['list.lock']
	del context['created_notes']
	del context['updated_notes']
	
def add_in_queue(context, result, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		context[queue_name].append(result)

def pop_queue(context, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		lst = context[queue_name]
		return lst.pop() if lst else None
			
def create_note(*args, **kwargs):
	context = kwargs['__context__']
	
	maxusers = context.as_int('max_temp_users', MAX_TEST_USERS)
	
	# create a ds client
	runner = kwargs['__runner__'] % maxusers
	username = 'test.user.%s@nextthought.com' % runner
	credentials = (username, 'temp001')
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	min_words = context.as_int('min_words', 10)
	max_words = context.as_int('max_words', 20)
	note_size = random.randint(min_words, max_words)
	
	# create a note
	nttype = generate_random_text()
	message = _generator.generate(note_size)
	container = generate_ntiid(nttype=nttype)
	result = TimerResultMixin()
	
	now = time.time()
	note = client.create_note(message, container=container)
	result['ds.op'] = time.time() - now
	result['words.note'] = note_size
	
	# check and save
	assert note, 'could  not create note'
	add_in_queue(context, (note, username, note_size), 'created_notes')
	
	return result

def update_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# get created note
	t = pop_queue(context, 'created_notes')
	if not t: return IGNORE_RESULT
	note, username, _ = t
	
	max_update_users = context.as_int('max_update_users', 0)
	if max_update_users:
		maxusers = context.as_int('max_temp_users', MAX_TEST_USERS)
		allusers = ['test.user.%s@nextthought.com' % x for x in range(1, maxusers+1)]
		sharedWith = random.sample(allusers, random.randint(1, max_update_users))
		if username in sharedWith:
			sharedWith.remove(username)
	else:
		sharedWith = []
		
	min_words = context.as_int('min_words', 10)
	max_words = context.as_int('max_words', 20)
	note_size = random.randint(min_words, max_words)
	
	# update note
	client = new_client(context)
	credentials = (username, 'temp001')
	client.set_credentials(credentials)
	
	note['body']=[_generator.generate(note_size)]
	note['sharedWith'] = sharedWith
	result = TimerResultMixin()
	
	now = time.time()
	note = client.update_object(note)
	result['ds.op'] = time.time() - now
	result['words.note'] = note_size
	result['shared.with'] = len(sharedWith)
	
	# check and save
	assert note, 'could not update note'
	add_in_queue(context,  (note, username, note_size), 'updated_notes')
	
	return result
	
def delete_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# get updated note
	t = pop_queue(context, 'updated_notes')
	if not t: return IGNORE_RESULT
	note, username, note_size = t
	
	# delete note
	client = new_client(context)
	credentials = (username, 'temp001')
	client.set_credentials(credentials)
	
	result = TimerResultMixin()
	now = time.time()
	client.delete_object(note)
	result['ds.op'] = time.time() - now
	result['words.note'] = note_size
	
	return result

