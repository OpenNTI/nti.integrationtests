#!/usr/bin/env python

import os
import sys
import argparse
import tempfile

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.runners import test_runner

def main(args = None):
	args = args or sys.argv[1:]

	parser = argparse.ArgumentParser(prog='General Purpose Tests')
	parser.add_argument('-uc', '--use_coverage', help='use coverage', action='store_true', default = False)
	parser.add_argument('-cr', '--coverage_report', help='create coverage report', action='store_true', default = False)
	parser.add_argument('-rd', '--root_dir', help='root directory', required=False)
	parser.add_argument('-p', '--port', help='server port', type=int, required=False, default=None)
	parser.add_argument('-sc', '--sync_changes', help='sync_changes', action='store_true', default = False)

	opts, rem_args = parser.parse_known_args(args) # Let Nose have the remainder of the args
	sys.argv = sys.argv[:1] + rem_args

	sync_changes = opts.sync_changes
	use_coverage = True if opts.use_coverage else False
	coverage_report = True if opts.coverage_report else False
	if os.getenv('DATASERVER_DIR_IS_BUILDOUT'):
		# We are running directly from an already setup
		# environment. Yay!
		root_dir = os.getenv('DATASERVER_DIR')
		port = os.getenv('DATASERVER_BUILDOUT_PORT')
	else:
		root_dir = opts.root_dir if opts.root_dir else tempfile.mkdtemp(prefix="ds.data.gpt.", dir="/tmp")
		port = opts.port if opts.port else get_open_port()

	# set env that are used in the test run
	os.environ['port'] = str(port)
	os.environ['root_dir'] = os.path.abspath(os.path.expanduser(root_dir))
	os.environ['use_coverage'] = 'True' if opts.use_coverage else 'False'
	if sync_changes:
		os.environ['DATASERVER_SYNC_CHANGES'] = 'True'

	import nti.integrationtests.generalpurpose.utils
	test_runner(module=nti.integrationtests.generalpurpose.utils, pattern="run_*.py", use_coverage=use_coverage,
				coverage_report=coverage_report, port=port, root_dir=root_dir)

if __name__ == '__main__':
	main(sys.argv[1:])
