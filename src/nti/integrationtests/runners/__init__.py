import time

from unittest import defaultTestLoader
from unittest import TextTestRunner

from nti.integrationtests.dataserver.server import DataserverProcess

def set_server_data(target, dsprocess):
	if hasattr(target, "__iter__"):
		for t in target:
			set_server_data(t, dsprocess)
	dsprocess.register_server_data(target)
	dsprocess.register_server_data(target.__class__)
		
def run_test_suite(suite, dsprocess, verbosity=2, use_coverage=False, coverage_report=False):
	try:
		if use_coverage:
			dsprocess.start_server_with_coverage()
			pass
		else:
			dsprocess.start_server()
		
		print "Waiting for server to come up...."
		
		time.sleep(5)
		
		print "Starting tests"
		
		set_server_data(suite, dsprocess)
		runner = TextTestRunner(verbosity=verbosity)
		runner.run(suite)
		
	finally:
		if use_coverage:
			dsprocess.terminate_server_with_coverage(report = coverage_report)
		else:
			dsprocess.terminate_server()
	
def test_runner(path, pattern="test*.py", use_coverage=False, coverage_report=False, 
				port=None, root_dir=None):
	
	suite = defaultTestLoader.discover(path, pattern)
	dsprocess = DataserverProcess(port=port, root_dir=root_dir)
	run_test_suite(suite, dsprocess, use_coverage=use_coverage, coverage_report=coverage_report)
