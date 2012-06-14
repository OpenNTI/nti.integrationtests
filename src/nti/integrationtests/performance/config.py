from __future__ import print_function, unicode_literals

import os
import ConfigParser
import multiprocessing

from zope.dottedname.resolve import resolve

from nti.integrationtests.utils import get_option
from nti.integrationtests.utils import get_int_option
from nti.integrationtests.utils import get_bool_option
from nti.integrationtests.utils import get_float_option

from nti.integrationtests.performance import noop
from nti.integrationtests.performance import Context
from nti.integrationtests.performance import RunnerGroup
from nti.integrationtests.performance import DelegateContext

import logging
logger = logging.getLogger(__name__)

# ====================
		
def is_default_value(config, section, name):
	def_val = config.defaults()[name] if name in config.defaults() else None
	sec_val = get_option(config, section, name)
	return def_val == sec_val
		
def read_config(config_file, process_args=True):
	
	logger.info("processing '%s'", config_file)
	
	group_runners = []
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	config_dir = os.path.dirname(config_file)
	config_name, _ = os.path.splitext(os.path.basename(config_file))
	
	# --------------
	
	def parse_items(context, config, process_args, section=ConfigParser.DEFAULTSECT):
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
	
	context.base_path = os.path.expanduser(get_option(config, name="base_path", default=config_dir))
	context.output_dir = get_option(config, name="output_dir", default=None)
	if context.output_dir:
		context.output_dir = os.path.join(context.base_path, context.output_dir)

	context.database_file = get_option(config, name="database_file", default=None)
	context.db_batch = get_bool_option(config, name="db_batch", default=False)
	
	if process_args:
		context.script_setup = resolve(context.script_setup) if hasattr(context, "script_setup") else noop 
		context.script_teardown = resolve(context.script_teardown) if hasattr(context, "script_teardown") else noop 
		context.script_subscriber = resolve(context.script_subscriber) if hasattr(context, "script_subscriber") else None 
		
	# read running groups
	
	context.run_time = get_int_option(config, name="run_time")
	context.rampup = get_int_option(config, name="rampup", default=0)
	context.use_threads = get_bool_option(config, name="use_threads")
	context.call_wait_time = get_float_option(config, name="call_wait_time", default=0)
	context.max_iterations = get_int_option(config, name="max_iterations")
	
	for num, section in enumerate(config.sections()):
		delegate = DelegateContext(context)
		parse_items(delegate, config, process_args, section)
		
		delegate.group_number = num
		delegate.group_name = get_option(config, section, 'group_name', section)
		delegate.rampup = get_int_option(config, section, 'rampup', context.rampup)
			
		delegate.run_time = get_int_option(config, section, 'run_time') \
							if not is_default_value(config, section, 'run_time') else None

		delegate.max_iterations = 	get_int_option(config, section, 'max_iterations') \
									if not is_default_value(config, section, 'max_iterations') else None
		
		if delegate.run_time:
			delegate.max_iterations = None
		elif delegate.max_iterations:
			delegate.run_time = None
			
		if not delegate.run_time and not delegate.max_iterations:
			delegate.run_time = context.run_time
			delegate.max_iterations = context.max_iterations
			
		delegate.runners = config.getint(section, 'runners')
		if delegate.runners > multiprocessing.cpu_count():
			logger.warn("number of runners for group '%s' is %s. CPU count (%s) exceeded",
						 delegate.group_name, delegate.runners, multiprocessing.cpu_count())
			
		delegate.target = config.get(section, 'target')
		delegate.target_args = get_option(config, section, 'target_args', None)
		
		delegate.use_threads = get_bool_option(config, section, "use_threads", context.use_threads)
		delegate.call_wait_time = get_float_option(config, section, "call_wait_time", context.call_wait_time)
		
		# get target and params
		if process_args:
			delegate.target = resolve(delegate.target)
			delegate.target_args = eval(delegate.target_args) if delegate.target_args else delegate.target_args
			
		# resolve setup/teardown
		if process_args:
			delegate.setup = resolve(delegate.setup) if hasattr(delegate, "setup") else noop 
			delegate.teardown = resolve(delegate.teardown) if hasattr(delegate, "teardown") else noop 
	
		runner = RunnerGroup(delegate, validate=process_args)
		group_runners.append(runner)
	
	if not process_args:
		context['config'] = config
		
	return (context, group_runners)
