#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import glob
import os
import sys
import time
import shutil
import socket
import tempfile
import subprocess
import ConfigParser
from datetime import datetime

logger = __import__('logging').getLogger(__name__)

from nti.integrationtests.utils import PORT
from nti.integrationtests.utils import SERVER_HOST
from nti.integrationtests.utils import get_int_option
from nti.integrationtests.utils import get_bool_option

# Must be extremely careful with this next one. Some clients
# assume they own it and can delete the entire thing, clearly not right,
# but cater to it by using a throw-away directory if one is not provided.
DATASERVER_DIR = os.getenv('DATASERVER_DIR') or os.path.join(tempfile.gettempdir(), 'DEFAULT_INT_TEST_DIR')
SERVER_CONFIG = os.getenv('SERVER_CONFIG', os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../config/development.ini")))
COVERAGE_CONFIG = os.getenv('COVERAGE_CONFIG', os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../config/coverage_run.cfg")))

class DataserverProcess(object):

	ENDPOINT = 'http://%s:%s/dataserver' % (SERVER_HOST, PORT)
	ENDPOINT2 = 'http://%s:%s/dataserver2' % (SERVER_HOST, PORT)

	SERVER_DELAY = 3
	KEY_TEST_WAIT= 'TEST_WAIT'

	@classmethod
	def resolve_endpoint(cls, host=SERVER_HOST, port=PORT, is_secure=False):
		port = port or PORT
		host = host or SERVER_HOST
		protocol = 'https' if is_secure else 'http'
		result = '%s://%s:%s/dataserver2' % (protocol, host, port)
		return result

	def __init__(self, port=PORT, root_dir=None):
		self.process = None
		self.port = int(port) if port else PORT
		self.endpoint = self.resolve_endpoint(SERVER_HOST, self.port)
		self.root_dir = os.path.abspath( os.path.expanduser(root_dir if root_dir else DATASERVER_DIR) )

	def register_server_data(self, target):
		target.port = self.port
		target.root_dir = self.root_dir
		target.endpoint = self.endpoint

	def is_running(self):
		return self._send_message(SERVER_HOST, self.port)
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

	def start_server(self, block_interval_seconds=0.5, max_wait_secs=60, *arg, **kwargs):
		self._start_process(block_interval_seconds, max_wait_secs, use_coverage=False, \
							root_dir=self.root_dir, port=self.port, **kwargs)

	startServer = start_server

	def start_server_with_coverage(self, block_interval_seconds=2, max_wait_secs=300, *arg, **kwargs):
		self._start_process(block_interval_seconds, max_wait_secs, use_coverage=True, \
							root_dir=self.root_dir, port=self.port, *arg, **kwargs)

	startServerWithCoverage = start_server_with_coverage

	def _start_process(self, block_interval_seconds=2, max_wait_secs=300, *arg, **kwargs):
		if self.process or self.is_running():
			logger.debug( "Dataserver already running.  Won't start a new one" )
		else:
			port = int(kwargs.get('port', PORT))
			sync_changes = kwargs.get('sync_changes', None)
			use_coverage = kwargs.get('use_coverage', False)
			coverage_rcfile = kwargs.get('rcfile', COVERAGE_CONFIG)
			root_dir = os.path.abspath( os.path.expanduser(kwargs.get('root_dir', DATASERVER_DIR)))
			pserve_ini_file = kwargs.get('pserve_ini_file', None) or SERVER_CONFIG

			logger.info( 'Starting dataserver (%s,%s)', port, root_dir)
			if not os.getenv('DATASERVER_DIR_IS_BUILDOUT'):
				pserve_ini_file = self._rewrite_pserve_config(	pserve_ini_file,
																root_dir=root_dir,
																port=port,
																sync_changes=sync_changes)
				if use_coverage:
					self._write_supervisor_config_coverage(root_dir, pserve_ini_file, coverage_rcfile)
				else:
					self._write_supervisor_config(root_dir, pserve_ini_file)


				# start server
				command = os.path.join(os.path.dirname(sys.executable), 'supervisord')
				args = [command, '-c', os.path.join(root_dir, 'etc', 'supervisord_dev.conf')]
			else:
				# buildout gives us a bin/supervisord that already
				# has the right executable and the right conf file.
				# We just don't want to spawn it in the background
				command = os.path.join(os.getenv('DATASERVER_DIR'), 'bin', 'supervisord' )
				args = [command, '-n']

			os.environ['DATASERVER_TESTING_PLAIN_TEXT_PWDS'] = 'True'
			devnull = open("/dev/null", 'w') if 'DATASERVER_NO_REDIRECT' not in os.environ else None
			self.process = subprocess.Popen(args, stdin=devnull, stdout=devnull, stderr=devnull)
			if devnull is not None:
				devnull.close()

			elapsed = 0
			while elapsed <= max_wait_secs and not self.isRunning():
				time.sleep(block_interval_seconds)
				elapsed = elapsed + block_interval_seconds

			if elapsed >= max_wait_secs:
				print("===============\nFailed to start server; server logs follow.")
				try:
					for filename in glob.iglob(os.path.join(os.getenv('DATASERVER_DIR'), 'var', 'log', 'pserve-std*' )):
						with open(filename, 'r') as f:
							print(f.read())
				except Exception:
					logger.exception("Failed to print log")
				print("===============\nDone with logs.")
				raise Exception("Could not start data server")

			if self.KEY_TEST_WAIT in os.environ:
				time.sleep( int( os.environ[self.KEY_TEST_WAIT] ) )
			else:
				time.sleep(block_interval_seconds)


	def _rewrite_pserve_config(	self,
								config_path,
								root_dir=DATASERVER_DIR,
								port=PORT,
								sync_changes=None,
								out_dir="/tmp"):

		if not os.path.exists(config_path):
			raise OSError('No pserve file %s' % config_path)

		result = config_path
		ini = ConfigParser.SafeConfigParser()
		ini.read(config_path)

		config_port = get_int_option(ini, name='http_port', default=PORT)
		config_sync_changes = get_bool_option(ini, name='sync_changes', default=True)
		sync_changes = config_sync_changes if sync_changes is None else sync_changes

		rewrite = config_port != port or sync_changes != config_sync_changes
		if config_port != port:
			ini.set('DEFAULT', 'http_port', str(port))

		if sync_changes != config_sync_changes:
			ini.set('DEFAULT', 'sync_changes', str(sync_changes))

		if rewrite:
			if not os.path.exists(out_dir):
				os.makedirs(out_dir)

			new_config = tempfile.mktemp(prefix="pserve.", suffix=".ini", dir=out_dir)
			with open(new_config, "wb") as fp:
				ini.write(fp)


			result = new_config

		if sync_changes:
			os.environ['DATASERVER_SYNC_CHANGES'] = 'True'

		return result

	def _rewrite_supervisor_config(self, config, command_prefix):

		if not os.path.exists(config):
			raise OSError('No supervisord file %s' % config)

		ini = ConfigParser.SafeConfigParser()
		ini.read(config)
		for section in ini.sections():
			if section.startswith("program:"):
				command = ini.get(section, 'command')
				if not command.startswith( '/' ):
					ini.set(section, 'command', command_prefix + command)

		with open(config, "wb") as fp:
			ini.write(fp)

	def _write_supervisor_config(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG):

		root_dir = os.path.expanduser(root_dir)
		if os.path.exists(root_dir):
			shutil.rmtree(root_dir, ignore_errors=False)

		if not os.path.exists(pserve_ini_file):
			raise OSError('No ini file %s' % pserve_ini_file)

		command = os.path.join(os.path.dirname(sys.executable), 'nti_init_env')
		args = [command, root_dir, pserve_ini_file, '--with-example']
		if subprocess.call(args) != 0:
			raise OSError('Error while creating configurations', args)

		command_prefix = os.path.dirname(sys.executable) + '/'
		etc_dir = os.path.join( os.path.abspath( os.path.expanduser(root_dir) ), 'etc' )
		visord = os.path.join(etc_dir, 'supervisord_dev.conf')
		self._rewrite_supervisor_config(visord, command_prefix)

		if os.path.exists( os.path.join( os.path.dirname( SERVER_CONFIG ), 'library.zcml' ) ):
			shutil.copyfile( os.path.join( os.path.dirname( SERVER_CONFIG ), 'library.zcml' ),
							 os.path.join( etc_dir, 'library.zcml' ) )


	def _write_supervisor_config_coverage(self, root_dir=DATASERVER_DIR, pserve_ini_file=SERVER_CONFIG,
										   rcfile=COVERAGE_CONFIG):

		if not os.path.exists(rcfile):
			raise OSError('No coverage file %s' % rcfile)

		self._write_supervisor_config(root_dir, pserve_ini_file)
		visord = os.path.join(os.path.expanduser(root_dir), 'etc', 'supervisord_dev.conf')
		command_prefix = ' '.join(['coverage', 'run', '--rcfile=%s' % rcfile, ''])
		command_prefix = os.path.join(os.path.dirname(sys.executable), command_prefix)
		self._rewrite_supervisor_config(visord, command_prefix)


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
				try:
					dt = datetime.now()
					s = "ds." + dt.strftime("%Y%m%d.%H%M")
					out_path = s + ".html"
					args = ['coverage', 'html', "--directory=%s" % out_path, "--rcfile=%s" % rcfile]
					subprocess.call(args)
				except:
					pass
		return result

	terminateServerWithCoverage = terminate_server_with_coverage

	def _terminate_process(self, block_interval_seconds=1, max_wait_secs=30):
		result = False
		if self.process:
			print('Terminating dataserver')
			try:
				self.process.terminate()
				result = self._wait_for_termination(block_interval_seconds, max_wait_secs)
				self.process = None if result else self.process
			except OSError as e:
				print('Failed to terminate dataserver', e)
				self.process = None # No use trying again
		return result

	def _wait_for_termination(self, block_interval_seconds=1, max_wait_secs=30):

		elapsed = 0
		while  elapsed <= max_wait_secs and self.is_running():
			time.sleep(block_interval_seconds)
			elapsed = elapsed + block_interval_seconds

		if elapsed >= max_wait_secs:
			print("Could not stop data server")
			return False

		return True
