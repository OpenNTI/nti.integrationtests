import time

from concurrent.futures import ProcessPoolExecutor

from nti.integrationtests.dataserver.client import DataserverClient

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

from hamcrest import assert_that
from hamcrest import has_length
from hamcrest import greater_than_or_equal_to

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def script_setup(context):
	init_server(context)
	prepare_containers(context)
	
def script_teardown(context):
	stop_server(context)

# -----------------------------------

def prepare_container(endpoint, user, notes):
	credentials = (user, 'temp001')
	container = generate_ntiid(provider=user, nttype=generate_random_text())
	client = DataserverClient(endpoint, credentials=credentials)
	for _ in xrange(notes):
		message = generate_message(3,3)
		client.create_note(message, container=container, credentials=credentials)
	return notes, container

def prepare_containers(context):
	result = {}
	user = 'test.user.1@nextthought.com'
	endpoint = context.endpoint
	containers_sizes = getattr(context, 'containers_sizes', (50,)) 
	
	t = time.time()
	logger.info("Preparing containers")
	with ProcessPoolExecutor() as executor:
		futures = []
		for n in containers_sizes:
			futures.append(executor.submit(prepare_container, endpoint, user, n))
			
		for future in futures:
			n, container = future.result()
			result[n] = container

	elapsed = time.time() - t
	logger.info("Containers has been filled. (%.3f)s", elapsed)			
	context['containers'] = result
	
# -----------------------------------

def get_ugd(container_size, **kwargs):
	context = kwargs['__context__']
	containers = context['containers']
	if not containers: 
		return IGNORE_RESULT
	
	container = containers[container_size]
	if not container: 
		return IGNORE_RESULT
	
	# create a ds client
	client = new_client(context)
	
	ugd = client.get_user_generated_data(container)
	assert_that(ugd['Items'], has_length(greater_than_or_equal_to(container_size)))
	
if __name__ == '__main__':
	logger = logging.getLogger('')
	
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')

	
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "ugd.cfg")
	run(config_file)

