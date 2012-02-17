import Queue
import multiprocessing

from nti.integrationtests.performance import IGNORE_RESULT
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
	result = client.create_note(generate_message(1,4), container=generate_ntiid(nttype=nttype))
	
	# check and save
	assert result, 'could  not create note'
	if save_in_queue: set_in_queue(context, result, 'created_notes')
	return result.toDataServerObject()

def update_note(save_in_queue=False):
	context = update_note.__context__
	
	# create a ds client
	client = new_client(context)
	
	# update the note
	note = get_from_queue(context, 'created_notes')
	if not note: return IGNORE_RESULT
	
	# uodate note
	note['body']=[generate_message(1,4)]
	result = client.update_object(note)
	
	# check and save
	assert result, 'could  not update note'
	if save_in_queue: set_in_queue(context, result, 'updated_notes')
	return result.toDataServerObject()
	
if __name__ == '__main__':
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "notes_config.cfg")
	run(config_file)