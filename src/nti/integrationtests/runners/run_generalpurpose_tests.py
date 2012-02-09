#!/usr/bin/env python
import os
import sys
import nti.integrationtests.generalpurpose.utils.run_tests as runner

def main(args = None):
	os.chdir(os.path.dirname(runner.__file__))
	runner.main(args)

if __name__ == '__main__':
	main(sys.argv[1:])
