from __future__ import print_function, unicode_literals

import random

from nltk import word_tokenize

from whoosh.analysis import STOP_WORDS

from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.nltk import default_message_generator
from nti.integrationtests.chat.simulation import MAX_TEST_USERS

_maxusers = 40
_generator = default_message_generator()

def script_setup(context):
	context['list.lock'] = context.manager.Lock()
	context['created_notes'] = context.manager.list()
	
def script_teardown(context):
	del context['list.lock']
	del context['created_notes']
	
def add_in_queue(context, result, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		context[queue_name].append(result)

def pop_queue(context, queue_name='created_notes'):
	lock = context['list.lock']
	with lock:
		lst = context[queue_name]
		return lst.pop() if lst else None
		
def create_note(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__'] % _maxusers
	username = 'test.user.%s@nextthought.com' % runner
	credentials = (username, 'temp001')
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	# create a note
	nttype = generate_random_text()
	message = _generator.generate(random.randint(10, 40))
	
	container = None
	ntiids = getattr(context,'ntiids',None)
	if ntiids:
		container = random.choice(ntiids)
	container = container or generate_ntiid(nttype=nttype)
	
	note = client.create_note(message, container=container)
	assert note, 'could not create note'
	
	add_in_queue(context, (username, container, message.lower()))
	
	return IGNORE_RESULT

def search_note(*args, **kwargs):
	context = kwargs['__context__']
	
	triplet = pop_queue(context)
	if not triplet: return IGNORE_RESULT
	
	username, ntiid, message = triplet
	
	client = new_client(context)
	credentials = (username, 'temp001')
	client.set_credentials(credentials)
	
	query = None
	splits = word_tokenize(message) 
	while not query or query in STOP_WORDS or len(query) < 3:
		query = random.choice(splits)

	d = client.unified_search(query, ntiid)
	assert d['Hit Count'] >0, 'could not find content/note with query "%s"' % query
	
	return IGNORE_RESULT
