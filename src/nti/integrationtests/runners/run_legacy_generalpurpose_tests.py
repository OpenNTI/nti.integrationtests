import os
from nti.integrationtests.runners import test_runner

def main(args = None):
	dirname = os.path.join(os.path.dirname( __file__ ), '..', 'legacy', 'generalpurpose')
	test_runner( path = dirname)

if __name__ == '__main__':
	main()
