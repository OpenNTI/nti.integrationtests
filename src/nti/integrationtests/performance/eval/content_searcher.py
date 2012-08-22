from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import generate_random_text

def script_setup(context):
	server = context.as_str("server", None)
	if not server:
		init_server(context)
	
def script_teardown(context):
	server = context.as_str("server", None)
	if not server:
		stop_server(context)
		
def search(*args, **kwargs):
	context = kwargs['__context__']
	#runner = kwargs['__runner__']
	ntiid = context.as_str('ntiid')
	
	client = new_client(context)
	text = generate_random_text(random.randint(5, 15))
	client.unified_search(text, ntiid)	
	return IGNORE_RESULT
