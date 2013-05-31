from __future__ import print_function, unicode_literals

import os
import glob
import random
import multiprocessing

from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.utils.dataurl import encode
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.contenttypes import CanvasUrlShape
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.nltk import default_message_generator

import logging
logger = logging.getLogger(__name__)

_maxusers = MAX_TEST_USERS
_message_generator = default_message_generator()

def script_setup(context):
	_list = None
	use_threads = context.as_bool('use_threads', False)
	if use_threads:
		_list = list()
	else:
		logging.warn("Creating a new  multiprocessing Manager")
		manager = multiprocessing.Manager()
		_list = manager.list()
	
	path = os.path.join(os.path.dirname(__file__), 'resources')
	pathname = os.path.join(path, 'img*.jpg')
	for img in glob.glob(pathname):
		with open(img, "rb") as fd:
			raw_bytes = fd.read()
		url = encode(raw_bytes, 'image/jpg')
		_list.append(url)

	context['_images'] = _list
	
def script_teardown(context):
	del context['_images']
	

def create_url_shapes(context, min_shapes=1, max_shapes=10):
	result = []
	images = context['_images']
	shapes = random.randint(min_shapes, max_shapes)
	for _ in xrange(shapes+1):
		url = random.choice(images)
		shape = CanvasUrlShape(url=url)
		result.append(shape)
	return result
		
def create_note(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__'] % _maxusers
	username = 'test.user.%s@nextthought.com' % runner
	credentials = (username, 'temp001')
	
	client = new_client(context)
	client.set_credentials(credentials)
	
	min_shapes = context.as_int('min_shapes', 1)
	max_shapes = context.as_int('max_shapes', 10)
	min_words = context.as_int('min_words', 10)
	max_words = context.as_int('max_words', 40)
	
	# create a note
	message = _message_generator.generate_message(random.randint(min_words, max_words))
	shapes = create_url_shapes(context, min_shapes, max_shapes)
	canvas = Canvas(shapeList=shapes)
	body = [message, canvas]

	nttype = generate_random_text()
	container = generate_ntiid(nttype=nttype)
	note = client.create_note(body, container=container)
	assert note, 'could not create note'
	
	return IGNORE_RESULT
