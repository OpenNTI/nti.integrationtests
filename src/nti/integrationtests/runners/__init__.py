import sys
import time
import nose.core
import nose.config
import nose.plugins.manager
from nose.loader import defaultTestLoader

from nti.integrationtests.dataserver.server import DataserverProcess

def set_server_data(target, dsprocess):
	import nti.integrationtests
	nti.integrationtests.DataServerTestCase.process = dsprocess
	dsprocess.register_server_data(nti.integrationtests.DataServerTestCase)

def run_test_suite(suite, dsprocess, config=None, module=None, use_coverage=False, coverage_report=False, verbose=False):
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
		_runner = None 
		_argv = [sys.argv[0], '--verbose'] if verbose else [sys.argv[0]]
		nose.core.run( config=config, testRunner=_runner, suite=suite, module=module, argv=_argv )
	finally:
		if use_coverage:
			dsprocess.terminate_server_with_coverage(report = coverage_report)
		else:
			dsprocess.terminate_server()

def test_runner(path=None, module=None, pattern="test*.py", use_coverage=False, coverage_report=False,
				port=None, root_dir=None, verbose=False):
	cfg_files = nose.config.all_config_files()
	manager = nose.plugins.manager.DefaultPluginManager()

	config = nose.config.Config( files=cfg_files, plugins=manager )
	config.configure( sys.argv )
	loader = defaultTestLoader(config)
	if path:
		suite = loader.loadTestsFromDir( path )
	elif module:
		suite = loader.loadTestsFromModule( module )
		
	dsprocess = DataserverProcess(port=port, root_dir=root_dir)
	run_test_suite(	suite, dsprocess, config=config, use_coverage=use_coverage,
					coverage_report=coverage_report, verbose=verbose)
