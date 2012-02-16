import os
import time
import UserDict
import ConfigParser

from zope.dottedname.resolve import resolve

from nti.integrationtests.performance import RunnerGroup

# ====================

class Context(object, UserDict.DictMixin):

	def __init__(self, data=None):
		self._data = {}
		self._data.update(data or {})

	def __contains__( self, key ):
		return key in self._data

	def __getitem__(self, key):
		return self._data[key] if key in self._data else None

	def __setitem__(self, key, val):
		self._data[key] = val

	def __delitem__(self, key):
		self._data.pop(key)

	def keys(self):
		return self._data.keys()
	
	def __str__( self ):
		return "%s(%s)" % (self.__class__.__name__,self._data)

	def __repr__( self ):
		return self.__str__()

# ====================

def get_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	try:
		return config.get(section, name)
	except:
		return default

def get_bool_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=False):
	try:
		return config.getboolean(section, name)
	except:
		return default
	
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
	
	context = Context()
	for k, v in config.items(ConfigParser.DEFAULTSECT):
		if k.endswith('_env'):
			k = k[:-4]
			v = os.environ.get(v)
			
		if k.endswith('_args'):
			v = eval(v)
			k = k[:-5]
		setattr(context, k, v)
	
	context.serialize = get_bool_option(config, name="serialize")
	context.output_dir = get_option(config, name="output_dir", default='/tmp')
	context.test_name = get_option(config, name="test_name", default='unknown-%s' % time.time())
	
	def noop(): pass
	context.setup = resolve(context.setup) if  hasattr(context, "setup") else noop 
	context.teardown = resolve(context.teardown) if  hasattr(context, "teardown") else noop 
	
	# read running groups
	
	default_run_time = get_option(config, name="run_time")
	default_rampup = int(get_option(config, name="rampup", default=0))
	default_use_threads = get_bool_option(config, name="use_threads")
	default_call_wait_time = float(get_option(config, name="call_wait_time", default=0))
	default_max_iterations = get_option(config, name="max_iterations")
	
	for section in config.sections():
		group_name = get_option(config, section, 'group_name', section)
		run_time = int(get_option(config, section, 'run_time', 0))
		max_iterations = int(get_option(config, section, 'max_iterations', 0))
		rampup = int(get_option(config, section, 'rampup', default_rampup))
		
		if run_time:
			max_iterations = None
		elif max_iterations:
			run_time = None
			
		if not run_time and not max_iterations:
			run_time = default_run_time
			max_iterations = default_max_iterations
			
		runners = config.getint(section, 'runners')
		target = config.get(section, 'target')
		target_args = get_option(config, section, 'target_args', None)
		
		use_threads = get_bool_option(config, section, "use_threads", default_use_threads)
		call_wait_time = float(get_option(config, section, "call_wait_time", default_call_wait_time))
		
		# get target and params
		target = resolve(target)
		target_args = eval(target_args) if target_args else ()
		
		# save the context
		target.__context__ = context
		
		runner = RunnerGroup(group_name = group_name,
							 run_time = run_time,
							 max_iterations = max_iterations,
							 target = target,
							 target_args =target_args,
							 num_runners = runners,
							 rampup = rampup,
							 use_threads = use_threads,
							 call_wait_time = call_wait_time)
		
		runner.__context__ = context
		
		group_runners.append(runner)
	
	
	return (context, group_runners)
