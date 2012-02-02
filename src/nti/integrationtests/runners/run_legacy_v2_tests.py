#!/usr/bin/env python

import tempfile

from nti.integrationtests.runners import run_test_suite
from nti.integrationtests.legacy.ServerTest_v2 import test_suite
from nti.integrationtests.dataserver.server import DataserverProcess

def main(port=None, root_dir=None):	
	root_dir = root_dir or tempfile.mkdtemp(prefix="ds.data.", dir="/tmp")
	dsprocess = DataserverProcess(port=port, root_dir=root_dir)
	run_test_suite (test_suite(), dsprocess)
			
if __name__ == '__main__':
	main()
