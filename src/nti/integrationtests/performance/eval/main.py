#!/usr/bin/env python

import os
import sys

from nti.integrationtests.utils import eval_bool
from nti.integrationtests.performance.runner import run

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def set_logger(debug=False):
	level = logging.INFO if not debug else logging.DEBUG
	logging.basicConfig(level, format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')
	
def main():
	argv = sys.argv[1:]
	config = os.path.expanduser(argv[0]) if argv else None
	if not config or not os.path.exists(config):
		raise Exception("must specify a valid config file")
	
	debug = str(argv[1]) if len(argv) > 1 else 'false'
	debug = eval_bool(debug)
	set_logger(debug)
	
	run(config)
	
if __name__ == '__main__':
	main()
