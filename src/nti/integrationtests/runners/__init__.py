import time

from unittest import defaultTestLoader
from unittest import TextTestRunner
from nti.integrationtests.dataserver.server import DataserverProcess

def test_runner(path, pattern="test*.py", use_coverage=False, coverage_report=False):
	
	suite = defaultTestLoader.discover(path, pattern)
	dsprocess = DataserverProcess()
	try:
		if use_coverage:
			dsprocess.startServerWithCoverage()
		else:
			dsprocess.startServer()
		
		print "Waiting for server to come up...."
		
		time.sleep(5)
		
		print "Starting tests"
		
		runner = TextTestRunner(verbosity=2)
		for test in suite:
			runner.run(test)
			
	finally:
		if use_coverage:
			dsprocess.terminateServerWithCoverage(report = coverage_report)
		else:
			dsprocess.terminateServer()
