import time
import Queue
import multiprocessing

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

def set_in_queue(context, result, queue_name='notes'):
	if not queue_name in context:
		context[queue_name] = multiprocessing.Queue()
	context[queue_name].put_nowait(result)
	
def get_from_queue(context, queue_name='notes'):
	try:
		if queue_name in context:
			return context[queue_name].get_nowait()
	except Queue.Empty:
		pass
	return None
	
def create_note(save_in_queue=False):
	context = create_note.__context__
	
	# create a ds client
	client = new_client(context)
	
	# create a note
	nttype = generate_random_text()
	message = generate_message(1,4)
	container = generate_ntiid(nttype=nttype)
	result = TimerResultMixin()
	
	now = time.time()
	note = client.create_note(message, container=container, adapt=False)
	result.set_timer('ds.io', time.time() - now)
	
	# check and save
	assert note, 'could  not create note'
	if save_in_queue: set_in_queue(context, note, 'created_notes')
	
	return result

def update_note(save_in_queue=False):
	context = update_note.__context__
		
	# update the note
	note = get_from_queue(context, 'created_notes')
	if not note: return IGNORE_RESULT
	
	# update note
	client = new_client(context)
	note['body']=[generate_message(1,4)]
	result = TimerResultMixin()
	
	now = time.time()
	note = client.update_object(note, adapt=False)
	result.set_timer('ds.io', time.time() - now)
	
	# check and save
	assert note, 'could  not update note'
	if save_in_queue: set_in_queue(context, note, 'updated_notes')
	
	return result
	
def delete_note():
	context = delete_note.__context__
		
	# update the note
	note = get_from_queue(context, 'updated_notes')
	if not note: return IGNORE_RESULT
	
	# delete note
	client = new_client(context)
	result = TimerResultMixin()
	
	now = time.time()
	client.delete_object(note)
	result.set_timer('ds.io', time.time() - now)
	
	return result

if __name__ == '__main__':
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "notes_config.cfg")
	run(config_file)