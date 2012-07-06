from __future__ import print_function, unicode_literals

import time

from nti.integrationtests.chat import generate_message
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import generate_ntiid


from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def script_setup(context):
	server = context.as_str("server", None)
	if not server:
		init_server(context)
	
def script_teardown(context):
	server = context.as_str("server", None)
	if not server:
		stop_server(context)
	
# -----------------------------------

_max_users = MAX_TEST_USERS

def share(users, *args, **kwargs):
	context = kwargs['__context__']
	client = new_client(context)
		
	nttype = generate_random_text()
	message = generate_message(k=3)
	container = generate_ntiid(nttype=nttype)
	note = client.create_note(message, container=container)
	assert note, 'could  not create note'	
	
	result = TimerResultMixin()
	note = client.create_note(message, container=container)
	for no in users:
		no = min(no, MAX_TEST_USERS-1) 
		sw = ['test.user.%s@nextthought.com' % x for x in range(2, no+2)]
		note['sharedWith'] = sw
		
		# share note
		now = time.time()
		shared_obj = client.update_object(note)
		elpased = time.time() - now
		assert shared_obj, 'could  not share note'
		
		# record time
		result['sop.%s' % no] = elpased
		
	return result
