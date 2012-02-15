import os
import time
import ConfigParser

from zope.dottedname.resolve import resolve

from nti.integrationtests.performance import RunnerGroup

def get_option(config, section=ConfigParser.DEFAULTSECT, name, default=None):
	try:
		return config.get(section, name)
	except:
		return default

def get_bool_option(config, section=ConfigParser.DEFAULTSECT, name):
	try:
		return config.getboolean(section, name)
	except:
		return False
	
def eval_args(args):
	result = []
	for arg in args or []:
		if isinstance(arg, basestring) and arg.startswith("$"):
			key = args[1:]
			arg = os.environ.get(key, '')
		result.append(arg)
			
def read_config(config_file):
	group_runners = []
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	
	# save all properties in a context object
	
	context = object()
	for k, v in config.items(ConfigParser.DEFAULTSECT):
		setattr(context, k, v)
	
	context.serialize = get_bool_option(config, name="serialize")
	context.output_dir = get_option(config, name="output_dir", '/tmp')
	context.test_name = get_option(config, name="test_name", 'unknown-%s' + time.time())
	
	def noop(): pass
	context.setup = resolve(context.setup) if  hasattr(context, "setup") else noop 
	context.teardown = resolve(context.teardown) if  hasattr(context, "teardown") else noop 
	
	# read running groups
	
	default_run_time = get_option(config, name="run_time")
	default_rampup = int(get_option(config, name="rampup", 0))
	default_use_threads = get_bool_option(config, name="use_threads")
	default_call_wait_time = int(get_option(config, name="call_wait_time", 0))
	
	for section in config.sections():
		group_name = get_option(config, section, 'group_name', section)
		run_time = int(get_option(config, section, 'run_time', default_run_time))
		rampup = int(get_option(config, section, 'rampup', default_rampup))
		runners = int(config.get(section, 'runners'))
		target = config.get(section, 'target')
		target_args = get_option(config, section, 'target_args', None)
		use_threads = get_option(config, name="use_threads", str(default_use_threads)) == 'True'
		call_wait_time = get_option(config, name="call_wait_time", default_call_wait_time)
		
		# get target and params
		target = resolve(target)
		target_args = eval(target_args) if target_args else ()
		target_args = eval_args(target_args)
		
		# save the context
		target.__context__ = context
		
		runner = RunnerGroup(group_name = group_name,
							 run_time = run_time,
							 target = target,
							 target_args =target_args,
							 num_runners = runners,
							 rampup = rampup,
							 use_threads = use_threads,
							 call_wait_time = call_wait_time)
		
		runner.__context__ = context
		
		group_runners.append(runner)
	
	
	return (context, group_runners)
