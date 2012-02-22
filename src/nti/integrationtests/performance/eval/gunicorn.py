import os
import tempfile
import ConfigParser

from nti.integrationtests.utils import get_int_option
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def change_workers(config_file, workers):
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	
	rewrite = False
	if 'server:main' in config.sections():
		config_workers = get_int_option(config, 'server:main', 'workers', 1)
		if int(workers) != config_workers:
			rewrite = True
			config.set('server:main', 'workers', str(workers))
		
	if rewrite:
		config_file = tempfile.mktemp(prefix="pserve.", suffix=".ini", dir='/tmp')
		with open(config_file, 'w') as fp:
			config.write(fp)
	
	return config_file

# -----------------------------------

def setup(context):
	config_file = getattr(context, 'pserve_ini_file', None)
	workers = getattr(context, 'workers', None)
	
	if config_file and workers:
		config_file = os.path.join(context.base_path, config_file)
		config_file = change_workers(config_file, int(workers))
		context.pserver_ini_file = config_file
		
	init_server(context)
	
def teardown(context):
	stop_server(context)
	
# -----------------------------------

def create_note(*args, **kwargs):
	context = kwargs['__context__']
	
	# create a ds client
	client = new_client(context)
	
	# create a note
	nttype = generate_random_text()
	message = generate_message(4,4)
	container = generate_ntiid(nttype=nttype)
	
	note = client.create_note(message, container=container)
	
	# check and save
	assert note, 'could  not create note'
	
	return None

if __name__ == '__main__':
	logger = logging.getLogger('')
	
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')

	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "gunicorn.cfg")
	run(config_file)


