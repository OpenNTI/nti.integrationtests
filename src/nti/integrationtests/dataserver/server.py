import os
import sys
import time
import shutil
import socket
import datetime
import subprocess
import ConfigParser

DEFAULT_USER_PASSWORD = 'temp001'

PORT = int(os.getenv('PORT', '8081'))
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
DATASERVER_DIR = os.getenv('DATASERVER_DIR', '~/tmp')
SERVER_CONFIG = os.getenv('SERVER_CONFIG', os.path.join(os.path.dirname(__file__), "../../../../config/development.ini"))
COVERAGE_CONFIG = os.getenv('COVERAGE_CONFIG', os.path.join(os.path.dirname(__file__), "../../../../config/coverage_run.cfg"))

class DataserverProcess(object):

	KEY_TEST_WAIT= 'TEST_WAIT'
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
		
	# -----------------------------------
	
	def start_server(self, block_interval_seconds=1, max_wait_secs=30):
		self._start_process(block_interval_seconds, max_wait_secs, use_coverage=False)

	startServer = start_server
		
	def start_server_with_coverage(self, block_interval_seconds=1, max_wait_secs=30):
		self._start_process(block_interval_seconds, max_wait_secs, use_coverage=True)

	startServerWithCoverage = start_server_with_coverage
	
	def _start_process(self, block_interval_seconds=1, max_wait_secs=30, *arg, **kwargs):

		if self.process or self.is_running():
			print 'Dataserver already running.  Won\'t start a new one'
		else:
			print 'Starting dataserver'
			rcfile = kwargs.get('rcfile', COVERAGE_CONFIG)
			use_coverage = kwargs.get('use_coverage', False)
			pserve_ini_file = kwargs.get('pserve_ini_file', SERVER_CONFIG)
			root_dir = os.path.expanduser(kwargs.get('root_dir', DATASERVER_DIR))
			
			if use_coverage:
				self._writer_config_coverage(root_dir, pserve_ini_file, rcfile)
			else:
				self._write_config(root_dir, pserve_ini_file)
			
			command = os.path.join(os.path.dirname(sys.executable), 'supervisord')
			args = [command, '-c', os.path.join(root_dir, 'etc', 'supervisord_dev.conf')]
			devnull = None #open("/dev/null", 'w') if 'DATASERVER_NO_REDIRECT' not in os.environ else None
			self.process = subprocess.Popen(args, stdin=devnull, stdout=devnull, stderr=devnull)
			if devnull is not None:
				devnull.close()

			elapsed = 0
			while elapsed <= max_wait_secs and not self.isRunning():
				time.sleep(block_interval_seconds)
				elapsed = elapsed + block_interval_seconds
	
			if elapsed >= max_wait_secs:
				raise Exception("Could not start data server")
	
			if self.KEY_TEST_WAIT in os.environ:
				time.sleep( int( os.environ[self.KEY_TEST_WAIT] ) )
		
	# -----------------------------------
	
	def _rewrite_config(self, config, command_prefix):
		
		if not os.path.exists(config):
			raise OSError('No supervisord file %s' % config)
		
		ini = ConfigParser.SafeConfigParser()
		ini.read(config)
		for section in ini.sections():
			if section.startswith("program:"):
				command = ini.get(section, 'command')
				ini.set(section, 'command', command_prefix + command)
				
		with open(config, "wb") as fp:
			ini.write(fp)
				
	def _write_config(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG):
		
		root_dir = os.path.expanduser(root_dir)
		if os.path.exists(root_dir):
			shutil.rmtree(root_dir, ignore_errors=False)
			
		if not os.path.exists(pserve_ini_file):
			raise OSError('No ini file %s' % pserve_ini_file)
		
		args = [sys.executable, '-m', 'nti.dataserver.config', root_dir, pserve_ini_file]
		if subprocess.call(args) != 0:
			raise OSError('Error while creating configurations')
	
		command_prefix = os.path.dirname(sys.executable) + '/'
		visord = os.path.join(os.path.expanduser(root_dir), 'etc', 'supervisord_dev.conf')
		self._rewrite_config(visord, command_prefix)
	
	def _writer_config_coverage(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG, rcfile=COVERAGE_CONFIG):
		
		if not os.path.exists(rcfile):
			raise OSError('No coverage file %s' % rcfile)
		
		self._write_config(root_dir, pserve_ini_file)
		visord = os.path.join(os.path.expanduser(root_dir), 'etc', 'supervisord_dev.conf')
		command_prefix = ' '.join(['coverage', 'run', '--rcfile=%s' % rcfile, ''])
		command_prefix = os.path.join(os.path.dirname(sys.executable), command_prefix)
		self._rewrite_config(visord, command_prefix)
	
	# -----------------------------------

	def terminate_server(self, block_interval_seconds=1, max_wait_secs=30):
		if self.process or self.is_running():
			return self._terminate_process(block_interval_seconds, max_wait_secs)
		return False

	terminateServer = terminate_server

	def terminate_server_with_coverage(self, block_interval_seconds=1, max_wait_secs=30, rcfile=COVERAGE_CONFIG, report=True):
		result = False
		if self.process or self.is_running():
			if self._terminate_process(block_interval_seconds, max_wait_secs):
				args = ['coverage', 'combine', "--rcfile=%s" % rcfile]
				result = subprocess.call(args) == 0 
			
			if result and report:
				dt = datetime.now()
				s = "ds." + dt.strftime("%Y%m%d.%H%M")
				try:
					out_path = s + ".html"
					args = ['coverage', 'html', "--directory=%s" % out_path, "--rcfile=%s" % rcfile]
					subprocess.call(args)
				except:
					pass
		return result

	terminateServerWithCoverage = terminate_server_with_coverage

	def _terminate_process(self, block_interval_seconds=1, max_wait_secs=30):
		print 'Terminating dataserver'
		self.process.terminate()
		result = self._wait_for_termination(block_interval_seconds, max_wait_secs)
		self.process = None if result else self.process
		return result
		
	def _wait_for_termination(self, block_interval_seconds=1, max_wait_secs=30):

		elapsed = 0
		while  elapsed <= max_wait_secs and self.is_running():
			time.sleep(block_interval_seconds)
			elapsed = elapsed + block_interval_seconds

		if elapsed >= max_wait_secs:
			print "Could not stop data server"
			return False

		return True
			
if __name__ == '__main__':
	dc = DataserverProcess()
	dc.start_server()
	time.sleep(10)
	dc.terminate_server()
	