from nti.integrationtests.generalpurpose.utils.run_tests import run_tests
from nti.integrationtests.dataserver.server import DataserverProcess

def main(args = None):	
	dsprocess = DataserverProcess()
	try:
		run_tests()
	finally:
		dsprocess.terminateServer()

if __name__ == '__main__':
	main()
