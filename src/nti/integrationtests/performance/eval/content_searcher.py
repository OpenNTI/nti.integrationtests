from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.chat import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS

_max_users = MAX_TEST_USERS
		
def search(*args, **kwargs):
	context = kwargs['__context__']
	ntiids = context.ntiids
	
	idx = random.randint(1, _max_users)
	credentials = ("test.user.%s@nextthought.com" % idx, 'temp001')
	client = new_client(context)
	client.set_credentials(credentials)
	
	text = None
	splits = generate_message(k=3).split() 
	while not text and text not in ('and', 'or', 'in', 'of'):
		text = random.choice(splits)
		
	client.unified_search(text, random.choice(ntiids))	
	return IGNORE_RESULT
