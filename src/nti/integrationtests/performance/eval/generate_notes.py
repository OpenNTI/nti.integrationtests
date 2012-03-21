from nti.integrationtests.dataserver.client import DataserverClient

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def script_setup(context):
	init_server(context)
	
def script_teardown(context):
	stop_server(context)

def create_note(*args, **kwargs):
	context = kwargs['__context__']
	endpoint = context.endpoint
	credentials = getattr(context, "credentials", None)
	
	if args:
		container = args[0]
		if len(args) >=2:
			credentials = args[1]
	else:
		nttype = generate_random_text()
		container = generate_ntiid(nttype=nttype)
	
	client = DataserverClient(endpoint, credentials=credentials)
	message = generate_message(1,4)
	note = client.create_note(message, container=container)
	assert note, 'could  not create note'	
	return IGNORE_RESULT


if __name__ == '__main__':
	import os
	logger = logging.getLogger('')
	
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')

	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "generate_notes.cfg")
	run(config_file)