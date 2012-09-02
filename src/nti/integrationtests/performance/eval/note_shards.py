from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.performance.eval.shards import is_running
from nti.integrationtests.performance.eval.shards import start_server
from nti.integrationtests.performance.eval.shards import terminate_server

from nti.integrationtests.chat import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_random_text

defaut_shards = 4
default_users = 10
default_workers = 1

def script_setup(context):
	host = context.as_str('server', 'localhost')
	port = context.as_int('port', '8081')
	if not is_running(host=host, port=port):
		workers = context.as_int('workers', default_workers)
		shards = context.as_int('shards', defaut_shards)
		users = context.as_int('users', default_users)
		db_user = context.as_str('db_user', 'root')
		db_password = context.as_str('db_password', '')
		process = start_server(db_user, db_password, port=port, shards=shards, workers=workers, users=users)
	else:
		process = None
	context['process'] = process
	
def script_teardown(context):
	process = context.get('process',None)
	if process:
		port = context.as_int('port', '8081')
		terminate_server(process, port=port)
		
def create_note_ugd(*args, **kwargs):
	context = kwargs['__context__']
	max_users = context.as_int('users', default_users)
	username = 'test.user.%s@nextthought.com' % random.randint(1, max_users)
	credentials = (username, 'temp001')
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	# create a note
	nttype = generate_random_text()
	message = generate_message(k=3)
	container = generate_ntiid(nttype=nttype)
	note = client.create_note(message, container=container)
	assert note, 'could not create note'
	
	return IGNORE_RESULT

