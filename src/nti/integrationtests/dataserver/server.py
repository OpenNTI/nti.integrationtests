import os
import sys
import time
import shutil
import socket

from nti.dataserver.config import write_configs

PORT = int(os.getenv('PORT', '8081'))
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
DATASERVER_DIR = os.getenv('DATASERVER_DIR', '~/tmp')
SERVER_CONFIG = os.getenv('SERVER_CONFIG', os.path.join(os.path.dirname(__file__), "../../../../config/development.ini"))
COVERAGE_CONFIG = os.getenv('COVERAGE_CONFIG', os.path.join(os.path.dirname(__file__), "../../../../config/coverage_run.cfg"))

class DataserverProcess(object):

	ENDPOINT = 'http://%s:%s/dataserver' % (SERVER_HOST, PORT)
	ENDPOINT2 = 'http://%s:%s/dataserver2' % (SERVER_HOST, PORT)
	SERVER_DELAY = 3

	def __init__(self):
		self.process = None

	def is_running(self):
		return self._send_message(SERVER_HOST, PORT)
	isRunning = is_running

	def _send_message(self, ip=SERVER_HOST, port=PORT, message=None, do_shutdown=True):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((ip, int(port)))
			if message:
				sock.send(message)

			if do_shutdown:
				sock.shutdown(2)

			return True
		except:
			return False
		finally:
			sock.close()
		
	def start_server(self, blockIntervalSeconds=1, maxWaitSeconds=30):
		self._start_process([sys.executable, path], blockIntervalSeconds, maxWaitSeconds)

	startServer = start_server
		
	def _start_process(self, block_interval_seconds=1, max_wait_secs=30, *arg, **kwargs):

		if self.process or self.isRunning():
			print 'Dataserver already running.  Won\'t start a new one'
			return

		print 'Starting dataserver'
		
	def _write_config(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG):
		
		root_dir = os.path.expanduser(root_dir)
		if os.path.exists(root_dir):
			shutil.rmtree(root_dir, ignore_errors=False)
			
		if not os.path.exists(pserve_ini_file):
			raise OSError('No ini file %s' % pserve_ini_file)
		
		env = write_configs(root_dir, pserve_ini_file)
		return env
	
	def _writer_config_coverage(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG, rcfile=COVERAGE_CONFIG):
		if not os.path.exists(rcfile):
			raise OSError('No coverage file %s' % rcfile)
		
		command_prefix = ' '.join(['coverage', 'run', '--rcfile=%s' % rcfile])
		env = self._write_config(root_dir, pserve_ini_file)	
		env.write_supervisor_conf_file(pserve_ini_file, command_prefix)
		return env		
			
if __name__ == '__main__':
	dc = DataserverProcess()
	dc._writer_config_coverage()

