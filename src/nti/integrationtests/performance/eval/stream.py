#import time

from concurrent.futures import ProcessPoolExecutor

from nti.integrationtests.dataserver.client import DataserverClient
#from nti.integrationtests.performance import IGNORE_RESULT
#from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
#from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

def script_setup(context):
	init_server(context)
	
def script_teardown(context):
	stop_server(context)

def prepare_streams(endpoint, users=10, notes=100):
	result = {}
	with ProcessPoolExecutor() as executor:
		futures = []
		for n in xrange(1, users+1):
			user = 'test.user.%s@nextthought.com' % n
			futures.append(executor.submit(prepare_user_stream, endpoint, user, notes))
			
		for future in futures:
			user, container = future.result()
			result[user] = container
	return result

def prepare_user_stream(endpoint, user, notes=100):
	credentials = (user, 'temp001')
	container = generate_ntiid(provider=credentials[0], nttype=generate_random_text())
	client = DataserverClient(endpoint, credentials=credentials)
	for _ in xrange(notes):
		message = generate_message(3,3)
		client.create_note(message, container=container, credentials=credentials)
	return user, container

if __name__ == '__main__':
	prepare_streams(endpoint = 'http://csanchez.local:8081/dataserver2')
