import time

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

def script_setup(context):
	init_server(context)
	context['list.lock'] = context.manager.Lock()
	context['created_notes'] = context.manager.list()
	context['updated_notes'] = context.manager.list()
	
def script_teardown(context):
	stop_server(context)
	del context['list.lock']
	del context['created_notes']
	del context['updated_notes']
	
def add_in_queue(context, result, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		context['created_notes'].append(result)

def pop_queue(context, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		lst = context['created_notes']
		return lst.pop() if lst else None
			
def create_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# create a ds client
	client = new_client(context)
	
	# create a note
	nttype = generate_random_text()
	message = generate_message(1,4)
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
	note['body']=[generate_message(1,4)]
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
	if not note: return 'shit'
	
	# delete note
	client = new_client(context)
	result = TimerResultMixin()
	
	now = time.time()
	client.delete_object(note)
	result['ds.op'] = time.time() - now
	
	return result

if __name__ == '__main__':
	import logging
	logger = logging.getLogger('')
	
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')

	
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "notes.cfg")
	run(config_file)
