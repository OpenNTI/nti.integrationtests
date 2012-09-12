from __future__ import print_function, unicode_literals

import time
import random

from concurrent.futures import ProcessPoolExecutor

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.nltk import default_message_generator
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_random_text

from hamcrest import (assert_that, has_length, greater_than_or_equal_to)

import logging
logger = logging.getLogger(__name__)

_generator = default_message_generator()

def script_setup(context):
	prepare_containers(context)

def prepare_container(context, idx=1, notes=50):
	client = new_client(context)
	user = 'test.user.%s@nextthought.com' % idx
	credentials = (user, 'temp001')
	container = generate_ntiid(provider=user, nttype=generate_random_text())
	for _ in xrange(notes):
		message = _generator.generate(random.randint(10, 30))
		client.create_note(message, container=container, credentials=credentials)
	return notes, container

def prepare_containers(context):
	result = {}
	containers_sizes = getattr(context, 'containers_sizes', {50:1}) 
	
	t = time.time()
	logger.info("Preparing containers")
	with ProcessPoolExecutor() as executor:
		futures = []
		for n, idx in containers_sizes.items():
			futures.append(executor.submit(prepare_container, context, idx, n))
			
		for future in futures:
			n, container = future.result()
			result[n] = container

	elapsed = time.time() - t
	logger.info("Containers has been filled. (%.3f)s", elapsed)			
	context['containers'] = result

def get_ugd(container_size, **kwargs):
	context = kwargs['__context__']
	containers = context['containers']
	if not containers: 
		return IGNORE_RESULT
	
	container = containers[container_size]
	if not container: 
		return IGNORE_RESULT
	
	containers_sizes = getattr(context, 'containers_sizes', {50:1}) 
	idx = containers_sizes.get(container_size, 1)
	user = 'test.user.%s@nextthought.com' % idx
	credentials = (user, 'temp001')
	
	# create a ds client
	client = new_client(context)
	client.set_credentials(credentials)
	
	func = client.get_user_generated_data
	if context.as_bool('recursive', False):
		func = client.get_recursive_user_generated_data
	ugd = func(container)
	assert_that(ugd['Items'], has_length(greater_than_or_equal_to(container_size)))


