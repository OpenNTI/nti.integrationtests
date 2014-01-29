#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import inspect
import ConfigParser
import multiprocessing

from zope import interface
from zope.dottedname.resolve import resolve as dottedname

from .context import Context
from .processing import noop
from .processing import RunnerGroup
from .context import DelegatedContext
from . import interfaces as mc_interfaces

DEFAULTSECT = ConfigParser.DEFAULTSECT

def _get_option(method, section, name, default):
	try:
		return method(section, name)
	except:
		return default

def get_option(config, section=DEFAULTSECT, name=None, default=None):
	return _get_option(config.get, section, name, default)

def get_bool_option(config, section=DEFAULTSECT, name=None, default=False):
	return _get_option(config.getboolean, section, name, default)

def get_int_option(config, section=DEFAULTSECT, name=None, default=None):
	return _get_option(config.getint, section, name, default)

def get_float_option(config, section=DEFAULTSECT, name=None, default=None):
	return _get_option(config.getfloat, section, name, default)

def is_default_value(config, section, name):
	def_val = config.defaults()[name] if name in config.defaults() else None
	sec_val = get_option(config, section, name)
	return def_val == sec_val
		
def resolve(name):
	result = dottedname(name) if name else noop
	assert callable(result) or inspect.isfunction(result)
	interface.alsoProvides(result, mc_interfaces.ICallable)
	return result

def read_config(config_file, process_args=True):
	
	logger.info("Processing '%s'", config_file)
	
	group_runners = []
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	config_dir = os.path.dirname(config_file)
	config_name, _ = os.path.splitext(os.path.basename(config_file))
	
	# --------------
	
	def parse_items(context, config, process_args, section=DEFAULTSECT):
		for k, v in config.items(section):
			if k.endswith('_env'):
				k = k[:-4]
				v = os.environ.get(v) if process_args else v
				
			if k.endswith('_args'):
				v = eval(v) if process_args else v
				k = k[:-5]
			setattr(context, k, v)
	
	# --------------
	
	context = Context()
	parse_items(context, config, process_args)
	
	context.serialize = get_bool_option(config, name="serialize")
	context.test_name = get_option(config, name="test_name", default=config_name)
	
	context.base_path = \
		os.path.expanduser(get_option(config, name="base_path", default=config_dir))

	context.output_dir = get_option(config, name="output_dir", default=None)
	if not context.output_dir:
		context.output_dir = os.path.join(context.base_path, context.test_name)
	
	if process_args:
		context.script_setup = resolve(getattr(context, 'script_setup', None))
		context.script_teardown = resolve(getattr(context, 'script_teardown', None))
		context.script_subscriber = resolve(getattr(context, 'script_subscriber', None))
		
	# read running groups
	
	context.runners = get_int_option(config, name='runners')
	context.run_time = get_int_option(config, name="run_time")
	context.rampup = get_int_option(config, name="rampup", default=0)
	context.use_threads = get_bool_option(config, name="use_threads")
	context.max_iterations = get_int_option(config, name="max_iterations")
	context.call_wait_time = get_float_option(config, name="call_wait_time", default=0)

	for num, section in enumerate(config.sections()):
		delegated = DelegatedContext(context)
		parse_items(delegated, config, process_args, section)
		
		delegated.group_number = num
		delegated.group_name = get_option(config, section, 'group_name', section)
		delegated.rampup = get_int_option(config, section, 'rampup', context.rampup)
			
		delegated.run_time = \
					get_int_option(config, section, 'run_time') \
					if not is_default_value(config, section, 'run_time') else None

		delegated.max_iterations = \
					get_int_option(config, section, 'max_iterations') \
					if not is_default_value(config, section, 'max_iterations') else None
		
		if delegated.run_time:
			delegated.max_iterations = None
		elif delegated.max_iterations:
			delegated.run_time = None
			
		if not delegated.run_time and not delegated.max_iterations:
			delegated.run_time = context.run_time
			delegated.max_iterations = context.max_iterations
			
		delegated.runners = config.getint(section, 'runners')
		if delegated.runners > multiprocessing.cpu_count():
			logger.warn("number of runners for group '%s' is %s. CPU count exceeded",
						 delegated.group_name, delegated.runners)
			
		delegated.target = config.get(section, 'target')
		delegated.target_args = get_option(config, section, 'target_args', None)
		
		delegated.use_threads = \
				get_bool_option(config, section, "use_threads", context.use_threads)

		delegated.call_wait_time = \
				get_float_option(config, section, "call_wait_time",
								 context.call_wait_time)
		
		delegated.hold_results = \
				get_bool_option(config, section, "hold_results", False)
			
		# get target and params
		if process_args:
			delegated.target = resolve(delegated.target)
			delegated.target_args = eval(delegated.target_args) \
			if delegated.target_args else delegated.target_args
			
		# resolve setup/teardown
		if process_args:
			delegated.setup = resolve(getattr(delegated, 'setup', None))
			delegated.teardown = resolve(getattr(delegated, 'teardown', None))
	
		runner = RunnerGroup(delegated, validate=process_args)
		group_runners.append(runner)
	
	if not process_args:
		context['__config__'] = config
		
	return (context, group_runners)
