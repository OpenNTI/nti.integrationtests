from __future__ import print_function, unicode_literals

import random
import multiprocessing

from nltk import word_tokenize

from whoosh.analysis import STOP_WORDS

from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.utils import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS

import logging
logger = logging.getLogger(__name__)

_maxusers = MAX_TEST_USERS

def script_setup(context):
	context['list.lock'] = multiprocessing.Lock()
	context['created_notes'] = list()
	
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
	message = generate_message()
	
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
	iteration = kwargs['__iteration__']
	runner = kwargs['__runner__'] 
	
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
		query = query[0:-1] if query.endswith('.') else query
	
	logger.debug("runner %s, iteration %s, searching %s" % (runner, iteration, query))
	d = client.unified_search(query, ntiid)
	assert d['Hit Count'] >0, 'could not find content/note with query "%s"' % query
	
	return IGNORE_RESULT
