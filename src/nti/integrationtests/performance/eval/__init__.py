from __future__ import print_function, unicode_literals

import os
import random
import tempfile

from nti.integrationtests import generate_ntiid
from nti.integrationtests.utils import get_open_port
from nti.integrationtests.utils import boolean_states
from nti.integrationtests.performance import Subscriber
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DataserverProcess

def init_server(context):
	
	port = context.as_int("port", get_open_port())
	base_path = context.as_str("base_path", None)
	
	tmp_dir = tempfile.mktemp(prefix="ds.data.", dir="/tmp")
	root_dir = os.path.expanduser(context.as_str("root_dir", tmp_dir))
	if base_path:
		root_dir = os.path.join(base_path, root_dir)
		
	use_coverage = getattr(context, "use_coverage", 'False')
	use_coverage = boolean_states.get(use_coverage.lower(), False)
	
	sync_changes = getattr(context, "sync_changes", None)
	sync_changes = boolean_states.get(sync_changes.lower(), None) if sync_changes is not None else None
	
	pserve_ini_file = getattr(context, "pserve_ini_file", None)
	if base_path and pserve_ini_file:
		pserve_ini_file = os.path.join(base_path, pserve_ini_file)
		pserve_ini_file = os.path.expanduser(pserve_ini_file)
	
	ds = DataserverProcess(port=port, root_dir=root_dir)
	context.__dataserver__ = ds
	context.endpoint = ds.endpoint
	
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
			
def new_client(context):
	endpoint = context.as_str("endpoint", None)
	if not endpoint:
		port =  context.as_int( "port", 8081)
		server =  context.as_str("server", 'localhost')
		is_secure = context.as_bool("is_secure", False)
		endpoint = DataserverProcess.resolve_endpoint(server, port, is_secure)
	
	credentials = getattr(context, "credentials", None)
	client = DataserverClient(endpoint=endpoint, credentials=credentials)
	return client

def generate_random_text(a_max=5):
	word = []
	for _ in xrange(a_max+1):
		word.append(chr(random.randint(ord('a'), ord('z'))))
	return "".join(word)

class SimpleStatSubscriber(Subscriber):
	def __init__(self, *args, **kwargs):
		Subscriber.__init__(self, *args, **kwargs)
		self.summary = {}
	
	def __call__(self, timestamp, group, result):
		name = group.group_name
		record = self.summary.get(name, None)
		if not record:
			# iteration, accum rum_time, average_run_time
			record = [0, 0, 0]
			self.summary[name] = record
			
		record[0] = record[0] + 1
		record[1] = record[1] + result.run_time
		record[2] = record[1] / record[0]
	
	def get_avg_run_time(self, group):
		record = self.summary.get(group, None)
		return record[2] if record else None
	
	def get_max_iterations(self, group):
		record = self.summary.get(group, None)
		return record[0] if record else None
	
