#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import time
import inspect
import logging
import argparse

import zope.exceptions
from zope import component

from .config import read_config
from . import interfaces as mc_interfaces
	
def get_result_listeners():
	for _, impl in component.getUtilitiesFor(mc_interfaces.IResultListener):
		yield impl

def open_result_listeners(context):
	for listener in get_result_listeners():
		component.provideHandler(listener, [mc_interfaces.IRunnerResult])
		listener.open(context)

def close_result_listeners(context):
	gsm = component.getGlobalSiteManager()
	for listener in get_result_listeners():
		listener.close(context)
		gsm.unregisterHandler(listener, [mc_interfaces.IRunnerResult])

def run(config_file):
	context, groups = read_config (config_file)
	context['config_file'] = config_file
	
	run_localtime = time.localtime()
	timestamp = time.strftime('%Y.%m.%d_%H.%M.%S', run_localtime)
	context.timestamp = timestamp
		
	clazz = context.script_subscriber
	if 	clazz and inspect.isclass(clazz) and \
		mc_interfaces.IResultListener.implementedBy(clazz):
		# register result listerner
		component.provideUtility(clazz(), mc_interfaces.IResultListener)

	open_result_listeners(context)
	results = {}
	context['_results'] = results
	context.script_setup(context=context)
	try:
		now = time.time()
		for group in groups:
			if not context.serialize:
				group.start()
			else:
				group.run()
			results[group.group_name] = group.results
			
		if not context.serialize:
			for group in groups:
				group.join()
		
		result = time.time() - now
		return result
	finally:
		context.script_teardown(context=context)
		close_result_listeners(context)

def set_logger(debug=False):
	ei = '%(asctime)s %(levelname)-5.5s [%(name)s][%(thread)d][%(threadName)s] %(message)s'
	logging.root.handlers[0].setFormatter(zope.exceptions.log.Formatter(ei))

	level = logging.INFO if not debug else logging.DEBUG
	logging.basicConfig(level=level, format=ei)

def main():
	arg_parser = argparse.ArgumentParser(description="Mechanize runner")
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action='store_true',
							 dest='verbose')
	arg_parser.add_argument('config', help="config file")
	args = arg_parser.parse_args()

	set_logger(args.verbose)
	config = args.config
	config = os.path.expanduser(config) if config else None
	if not config or not os.path.exists(config):
		raise Exception("must specify a valid config file")

	return run(config)

if __name__ == '__main__':
	main()
