from __future__ import print_function, unicode_literals

import random
from whoosh.analysis import STOP_WORDS

from nltk import word_tokenize

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.nltk import default_message_generator

_max_users = MAX_TEST_USERS
_generator = default_message_generator()
		
def search(*args, **kwargs):
	context = kwargs['__context__']
	ntiids = context.ntiids
	
	idx = random.randint(1, _max_users)
	credentials = ("test.user.%s@nextthought.com" % idx, 'temp001')
	client = new_client(context)
	client.set_credentials(credentials)
	
	text = None
	message = _generator.generate(random.randint(10, 30))
	splits = word_tokenize(message)
	while not text or text in STOP_WORDS or len(text) < 3:
		text = random.choice(splits)
		
	client.unified_search(text, random.choice(ntiids))	
	return IGNORE_RESULT
