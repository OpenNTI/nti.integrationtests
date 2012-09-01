from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.nltk import default_message_generator
from nti.integrationtests.performance.eval import generate_ntiid

from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
_max_users = MAX_TEST_USERS
_generator = default_message_generator()

def create_note(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']
	
	idx = runner % _max_users  
	credentials = ("test.user.%s@nextthought.com" % idx, "temp001")
	if args:
		container = args[0]
	else:
		nttype = generate_random_text()
		container = generate_ntiid(nttype=nttype)
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	message = _generator.generate(random.randint(10, 30))
	note = client.create_note(message, container=container)
	assert note, 'could  not create note'	
	return IGNORE_RESULT
