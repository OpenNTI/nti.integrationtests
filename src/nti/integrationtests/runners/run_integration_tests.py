#!/usr/bin/env python

import os
import sys
import tempfile 
import argparse

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.runners import test_runner

def main(args = None):
	
	args = args or sys.argv[1:]
		
	parser = argparse.ArgumentParser(prog='Integration Tests')
	parser.add_argument('-uc', '--use_coverage', help='use coverage', action='store_true', default = False)
	parser.add_argument('-cr', '--coverage_report', help='create coverage report', action='store_true', default = False)
	parser.add_argument('-rd', '--root_dir', help='root directory', required=False)
	parser.add_argument('-p', '--port', help='server port', type=int, required=False, default=None)
	parser.add_argument('-sc', '--sync_changes', help='sync_changes', action='store_true', default = False)
	opts = parser.parse_args(args)

	sync_changes = opts.sync_changes
	use_coverage = True if opts.use_coverage else False
	coverage_report = True if opts.coverage_report else False
	root_dir = opts.root_dir if opts.root_dir else tempfile.mkdtemp(prefix="ds.data.int.", dir="/tmp")
	port = opts.port if opts.port else get_open_port()
	
	if sync_changes:
		os.environ['DATASERVER_SYNC_CHANGES'] = 'True'
		
	dirname = os.path.join(os.path.dirname( __file__ ), '..', 'integration')
	test_runner(path=dirname, use_coverage=use_coverage, coverage_report=coverage_report,
				port=port, root_dir=root_dir)

if __name__ == '__main__':
	main()
	