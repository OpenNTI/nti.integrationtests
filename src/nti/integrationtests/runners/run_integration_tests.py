#!/usr/bin/env python

import os
import sys
import argparse

from nti.integrationtests.runners import test_runner

def main(args = None):
	
	args = args or sys.argv[1:]
		
	parser = argparse.ArgumentParser(prog='Integration Tests')
	parser.add_argument('-uc', '--use_coverage', help='use coverage', action='store_true', default = False)
	parser.add_argument('-cr', '--coverage_report', help='create coverage report', action='store_true', default = False)
	opts = parser.parse_args(args)

	use_coverage = True if opts.use_coverage else False
	coverage_report = True if opts.coverage_report else False
	
	dirname = os.path.join(os.path.dirname( __file__ ), '..', 'integration')
	test_runner( path = dirname, use_coverage=use_coverage, coverage_report=coverage_report)

if __name__ == '__main__':
	main()
