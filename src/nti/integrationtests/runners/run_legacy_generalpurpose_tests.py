import os

from nti.integrationtests.runners import test_runner
from nti.integrationtests.dataserver.server import DataserverProcess

def main(args = None):
	dirname = os.path.join(os.path.dirname( __file__ ), '..', 'legacy', 'generalpurpose')
	dsprocess = DataserverProcess()
	try:
		test_runner( path = dirname)
	finally:
		dsprocess.terminateServer()

if __name__ == '__main__':
	main()
