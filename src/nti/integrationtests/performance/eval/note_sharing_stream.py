from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.chat import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
_max_users = MAX_TEST_USERS
		
def create_share(*args, **kwargs):
	context = kwargs['__context__']
	runner =  kwargs['__runner__']
	user = 'test.user.%s@nextthought.com' % runner
		
	client = new_client(context)
	credentials = (user, 'temp001')
	client.set_credentials(credentials)
	
	sharedWith = []
	for _ in xrange(random.randint(3, 10)):
		idx = random.randint(1,_max_users)
		if idx != runner:
			user = 'test.user.%s@nextthought.com' % idx
			sharedWith.append(user)
			
	nttype = generate_random_text()
	message = generate_message(k=3)
	container = generate_ntiid(nttype=nttype)
	note = client.create_note(message, container=container, sharedWith=sharedWith)
	assert note, 'could not create note'

	for _ in xrange(random.randint(1, len(sharedWith))):
		user = random.choice(sharedWith)
		credentials = (user, 'temp001')
		
		d = client.get_recursive_stream_data(container, credentials=credentials)
		items = d['Items']
		found = False
		for c in items:
			if c.cid == note.id:
				found = True
				break
		assert found, '%s not found in stream for user %s' % (note.id, user)
	
	return IGNORE_RESULT
