# -*- coding: utf-8 -*-
"""
Integration test runner module.

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

import sys
import time
import inspect
import unittest

import nose.core
import nose.config
import nose.plugins.manager

from nose.util import isclass
from nose.suite import ContextSuite
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

		print("Waiting for server to come up....")
		time.sleep(5)
		print("Starting tests")

		set_server_data(suite, dsprocess)

		_runner = None
		_argv = [sys.argv[0]]
		if verbose:
			_argv.append('--verbose')

		nose.core.run(config=config, testRunner=_runner, suite=suite, module=module, argv=_argv)
	finally:
		if use_coverage:
			dsprocess.terminate_server_with_coverage(report=coverage_report)
		else:
			dsprocess.terminate_server()

def _find_level(suite):
	context = suite.context
	pred = lambda x : isclass(x) and issubclass(x, unittest.TestCase)
	for _, item in inspect.getmembers(context, pred):
		level = getattr(item, 'level', None)
		if level is not None:
			return str(level)
	return None

def test_runner(path=None, module=None, pattern="test*.py", use_coverage=False, coverage_report=False,
				port=None, root_dir=None, levels=None, verbose=False):

	cfg_files = nose.config.all_config_files()
	manager = nose.plugins.manager.DefaultPluginManager()

	suite = config = nose.config.Config(files=cfg_files, plugins=manager)
	config.configure(sys.argv)

	loader = defaultTestLoader(config)
	if path:
		suite = loader.loadTestsFromDir(path)
	elif module:
		suite = loader.loadTestsFromModule(module)

	if levels:
		tests = []
		for s in suite:
			level = _find_level(s)
			if level and level in levels:
				tests.append(s)

		if tests:
			suite = ContextSuite(tests, context=suite.context, factory=suite.factory,
								 config=suite.config, resultProxy=suite.resultProxy, can_split=suite.can_split)
		else:
			return

	dsprocess = DataserverProcess(port=port, root_dir=root_dir)
	run_test_suite(suite, dsprocess, config=config, use_coverage=use_coverage,
 				   coverage_report=coverage_report, verbose=verbose)
