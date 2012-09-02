from __future__ import print_function, unicode_literals

import os
import sys
import time
import socket
import tempfile
import subprocess
import multiprocessing

from concurrent.futures import ThreadPoolExecutor

from nti.dataserver.utils.nti_init_shard import init_shard  as init_ds_shard
from nti.dataserver.utils.nti_create_user import create_user as create_ds_user

from nti.integrationtests.performance.eval.shards._config import get_port
from nti.integrationtests.performance.eval.shards._config import get_default_config
from nti.integrationtests.performance.eval.shards._dao import prepare as prepare_db
from nti.integrationtests.performance.eval.shards._config import prepare as prepare_config

import logging
logger = logging.getLogger(__name__)

def send_message(host='localhost', port=8081, message=None, do_shutdown=True):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((host, int(port)))
		if message:
			sock.send(message)

		if do_shutdown:
			sock.shutdown(2)

		return True
	except:
		return False
	finally:
		sock.close()

def is_running(host='localhost', port=8081):
	return send_message(host, port)
	
def start_server(config=None, env_dir=None, port=None):
	config = config or get_default_config()
	port = port or get_port(config)
	if not is_running(port=port):
		logger.info("starting server")
		
		assert env_dir, 'no env directory'
		env_dir = os.path.expanduser(env_dir)
		os.environ['DATASERVER_DIR'] = env_dir
		
		command = os.path.join(os.path.dirname(sys.executable), 'pserve')
		args = [command, config]
		devnull = open("/dev/null", 'w') if 'DATASERVER_NO_REDIRECT' not in os.environ else None
		process = subprocess.Popen(args, stdin=devnull, stdout=devnull, stderr=devnull)
		if devnull is not None:
			devnull.close()
		return process
	else:
		return None
			
def terminate_server(process=None, config=None, port=None, max_wait_secs=30):
	result = False
	if process:
		logger.info("terminating server")
		elapsed = 0
		config = config or get_default_config()
		port = port or get_port(config)
		process.terminate()
		while  elapsed <= max_wait_secs and is_running(port=port):
			time.sleep(1)
			elapsed = elapsed + 1
		result = elapsed <= max_wait_secs
		
		if result:
			logger.info("server terminated successfully")
		else:
			logger.info("could not terminate server")
			
	return result

def create_user(env_dir, username, password='temp001'):
	logger.info("creating user %s" % username)
	create_ds_user([env_dir, username, password])
	
def create_users(env_dir, users):
	with ThreadPoolExecutor(multiprocessing.cpu_count()) as pool:
		for x in range(1, users+1):
			username = 'test.user.%s@nextthought.com' % x
			pool.submit(create_user,  env_dir, username)
	
def init_shard(env_dir, shard_name):
	logger.info("initializing shard %s" % shard_name)
	init_ds_shard(env_dir, shard_name)

def init_shards(env_dir, shards=4, prefix='Users'):
	for x in range(1, shards+1):
		shard_name = '%s_%s' % (prefix, x)
		init_shard(env_dir, shard_name)

def _wait_for(host='localhost', port=8081, for_running=True, max_wait=30):
	elapsed = 0
	while elapsed < max_wait:
		running = is_running(host, port) 
		if (running and for_running) or (not running and not for_running): 
			break
		time.sleep(1)
		elapsed = elapsed  + 1
	return elapsed < max_wait
		
def prepare(user, password, shards=4, port=8081, workers=1, users=10, env_dir=None):
	env_dir = env_dir or tempfile.mkdtemp(prefix="ntids.", dir="/tmp")
	config = prepare_config(port=port, workers=workers, shards=shards, out_dir=env_dir)
	if not is_running(port=port):
		# initialize db
		prepare_db(user=user, password=password, shards=shards)
		# start dataserver
		process = start_server(config=config, env_dir=env_dir, port=port)
		try:
			if _wait_for(port=port):
				time.sleep(2) # wait a bit
				# init shards
				init_shards(env_dir, shards=shards)
				#create users
				create_users(env_dir, users)
		except:
			if process: process.terminate()
			raise
		return process
	else:
		return None
	
if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')
	prepare('root', 'saulo213')
	