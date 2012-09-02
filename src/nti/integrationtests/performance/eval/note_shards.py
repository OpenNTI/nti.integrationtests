from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.chat import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.integration import object_from_container
from nti.integrationtests.performance.eval.shards import is_running
from nti.integrationtests.performance.eval.shards import start_server
from nti.integrationtests.performance.eval import generate_random_text
from nti.integrationtests.performance.eval.shards import terminate_server

from hamcrest import (assert_that, has_length, greater_than_or_equal_to)

defaut_shards = 4
default_users = 10
default_workers = 1

def script_setup(context):
	host = context.as_str('server', 'localhost')
	port = context.as_int('port', 8081)
	if not is_running(host=host, port=port):
		workers = context.as_int('workers', default_workers)
		shards = context.as_int('shards', defaut_shards)
		users = context.as_int('users', default_users)
		db_user = context.as_str('db_user', 'root')
		db_password = context.as_str('db_password', '')
		env_dir = context.as_str('env_dir', None)
		process = start_server(db_user, db_password, port=port, shards=shards,
							   workers=workers, users=users, env_dir=env_dir)
	else:
		process = None
	context['process'] = process
	
def script_teardown(context):
	process = context.get('process',None)
	if process:
		port = context.as_int('port', 8081)
		terminate_server(process, port=port)
		
def note_operations(*args, **kwargs):
	context = kwargs['__context__']
	max_users = context.as_int('users', default_users)
	username = 'test.user.%s@nextthought.com' % random.randint(1, max_users)
	credentials = (username, 'temp001')
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	# create a note
	nttype = generate_random_text()
	message = generate_message()
	container = generate_ntiid(nttype=nttype)
	note = client.create_note(message, container=container)
	assert note, 'could not create note'
	
	message = generate_message()
	note['body']=[generate_message(k=3)]
	note = client.update_object(note)
	assert note, 'could not update note'
	
	shared = None
	while shared != username:
		shared = 'test.user.%s@nextthought.com' % random.randint(1, max_users)
	note['sharedWith'] = [shared]
	note = client.update_object(note)
	assert note, 'could not share note'
	
	# check in stream
	credentials = (shared, 'temp001')
	data = client.get_recursive_user_generated_data(container, credentials=credentials)
	assert_that(data['Items'], has_length(greater_than_or_equal_to(1)))
	shared_note = object_from_container(data, note)
	assert shared_note, 'could not find shared note'
	
	# remove
	credentials = (username, 'temp001')
	client.delete_object(note, credentials=credentials)
	
	return IGNORE_RESULT

