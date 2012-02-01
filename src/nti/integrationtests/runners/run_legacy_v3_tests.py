#!/usr/bin/env python

from nti.integrationtests.legacy.ServerTest_v3_quizzes import main as run_tests
from nti.integrationtests.dataserver.server import DataserverProcess

def main(args = None):	
	dsprocess = DataserverProcess()
	try:
		run_tests()
	finally:
		dsprocess.terminateServer()
		
if __name__ == '__main__':
	main()
