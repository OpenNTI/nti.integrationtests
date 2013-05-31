from __future__ import print_function, unicode_literals

import os
import random
import tempfile

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.utils import boolean_states
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DataserverProcess

def init_server(config):
	
	port = config['port']
	
	tmp_dir = tempfile.mktemp(prefix="ds.data.", dir="/tmp")
	root_dir = os.path.expanduser(tmp_dir)
		
	use_coverage = config.get('use_coverage', False)

	sync_changes = config.get('sync_changes', None)

	pserve_ini_file = config.get('pserve_ini_file', None)
	
	ds = DataserverProcess(port=port, root_dir=root_dir)
	config['__dataserver__'] = ds
	config['endpoint'] = ds.endpoint
	
	if not use_coverage:
		ds.start_server(sync_changes=sync_changes, pserve_ini_file=pserve_ini_file)
	else:
		ds.start_server_with_coverage(sync_changes=sync_changes, pserve_ini_file=pserve_ini_file)

def stop_server(context):
	ds = getattr(context, "__dataserver__", None)
	use_coverage = getattr(context, "use_coverage", 'False')
	use_coverage = boolean_states.get(use_coverage.lower(), False)
	
	if ds:
		if not use_coverage:
			ds.terminate_server()
		else:
			ds.terminate_server_with_coverage()
			
def new_client(config):
	endpoint = config.get('endpoint', None)
	if not endpoint:
		port =  config['port']
		server =  config['server']
		is_secure = config['is_secure']
		endpoint = DataserverProcess.resolve_endpoint(server, port, is_secure)
	
	credentials = config.get('credentials', None)
	client = DataserverClient(endpoint=endpoint, credentials=credentials)
	return client
	
