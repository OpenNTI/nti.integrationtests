from __future__ import print_function, unicode_literals

import time
import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.nltk import default_message_generator
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_random_text

_generator = default_message_generator()

def script_setup(context):
	context['list.lock'] = context.manager.Lock()
	context['created_notes'] = context.manager.list()
	context['updated_notes'] = context.manager.list()
	
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

