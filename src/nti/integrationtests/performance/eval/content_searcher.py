from __future__ import print_function, unicode_literals

from nti.integrationtests.dataserver.client import DataserverClient

from nti.integrationtests.chat import generate_message
from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import generate_ntiid

from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def script_setup(context):
	init_server(context)
	
def script_teardown(context):
	stop_server(context)

def searcher(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']
	ntiid =  kwargs['__runner__']
	endpoint = context.endpoint
	credentials = getattr(context, "credentials", None)
	
	if args:
		container = args[0]
		if len(args) >=2:
			credentials = args[1]
			if '%s' in credentials[0]:
				credentials = (credentials[0] % runner, credentials[1])
	else:
		nttype = generate_random_text()
		container = generate_ntiid(nttype=nttype)
	
	client = DataserverClient(endpoint, credentials=credentials)
	message = generate_message(k=3)
	note = client.create_note(message, container=container)
	assert note, 'could  not create note'	
	return IGNORE_RESULT
