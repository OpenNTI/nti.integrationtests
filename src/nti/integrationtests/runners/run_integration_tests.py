# -*- coding: utf-8 -*-
"""
Integration test runner.

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

from nti.monkey import gevent_patch_on_import
gevent_patch_on_import.patch()

import sys
import argparse
import tempfile

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.runners import test_runner

def main(args=None):

	args = args or sys.argv[1:]

	parser = argparse.ArgumentParser(prog='Integration Tests')
	parser.add_argument('-uc', '--use_coverage', help='use coverage', action='store_true', default=False)
	parser.add_argument('-cr', '--coverage_report', help='create coverage report', action='store_true', default=False)
	parser.add_argument('-rd', '--root_dir', help='root directory', required=False)
	parser.add_argument('-p', '--port', help='server port', type=int, required=False, default=None)
	parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False)
	parser.add_argument('-l', '--levels',
						 nargs="*",
						 dest='levels',
						 help="The test levels")

	opts, rem_args = parser.parse_known_args(args)  # Let Nose have the remainder of the args
	sys.argv = sys.argv[:1] + rem_args

	levels = opts.levels
	use_coverage = True if opts.use_coverage else False
	coverage_report = True if opts.coverage_report else False
	root_dir = os.path.abspath( os.path.expanduser(opts.root_dir if opts.root_dir else tempfile.mkdtemp(prefix="ds.data.int.", dir="/tmp") ) )
	port = opts.port if opts.port else get_open_port()

	import nti.integrationtests.integration
	test_runner(module=nti.integrationtests.integration, use_coverage=use_coverage, coverage_report=coverage_report,
 				port=port, root_dir=root_dir, levels=levels, verbose=opts.verbose)

if __name__ == '__main__':
	main()
