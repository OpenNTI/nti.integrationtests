from __future__ import print_function, unicode_literals

import time
import random
import multiprocessing

from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.nltk import default_message_generator

import logging
logger = logging.getLogger(__name__)

_generator = default_message_generator()

def script_setup(context):
	_list_1, _list_1 = _lock = None
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
	
	# create a ds client
	client = new_client(context)
	
	# create a note
	nttype = generate_random_text()
	message = _generator.generate(random.randint(10, 20))
	container = generate_ntiid(nttype=nttype)
	result = TimerResultMixin()
	
	now = time.time()
	note = client.create_note(message, container=container)
	result['ds.op'] = time.time() - now
	
	# check and save
	assert note, 'could  not create note'
	add_in_queue(context, note, 'created_notes')
	
	return result

def update_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# get created note
	note = pop_queue(context, 'created_notes')
	if not note: return IGNORE_RESULT
	
	# update note
	client = new_client(context)
	note['body']=[_generator.generate(random.randint(10, 20))]
	result = TimerResultMixin()
	
	now = time.time()
	note = client.update_object(note)
	result['ds.op'] = time.time() - now
	
	# check and save
	assert note, 'could not update note'
	add_in_queue(context, note, 'updated_notes')
	
	return result
	
def delete_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# get updated note
	note = pop_queue(context, 'updated_notes')
	if not note: return 'bad'
	
	# delete note
	client = new_client(context)
	result = TimerResultMixin()
	
	now = time.time()
	client.delete_object(note)
	result['ds.op'] = time.time() - now
	
	return result

