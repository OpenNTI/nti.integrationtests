import os
import time
import UserDict
import ConfigParser

from zope.dottedname.resolve import resolve

from nti.integrationtests.performance import RunnerGroup

# ====================

read_only_attributes = ('setup', 'teardown' )

default_attributes = (	'rampup', 'run_time','test_name', 'output_dir', 'serialize','use_threads',
					'max_iterations', 'call_wait_time') + read_only_attributes

group_attributes = ('runners', 'target', 'target_args')

# ====================

class Context(object, UserDict.DictMixin):

	def __init__(self, data=None):
		self._data = data or {}

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


class DelegateContext(Context):

	def __init__(self, context):
		super(DelegateContext, self).__init__(context._data)
		self.__dict__['delegate'] = context
			
	def __getattr__(self, name):
		return getattr(self.__dict__['delegate'],name)
	
	def __setattr__(self, name, value):
		if name not in read_only_attributes:
			self.__dict__[name] = value

# ====================

def _get_option(method, section, name, default):
	try:
		return method(section, name)
	except:
		return default
	
def get_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.get, section, name, default)

def get_bool_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=False):
	return _get_option(config.getboolean, section, name, default)

def get_int_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.getint, section, name, default)

def get_float_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.getfloat, section, name, default)
		
def is_default_value(config, section, name):
	def_val = config.defaults()[name] if name in config.defaults() else None
	sec_val = get_option(config, section, name)
	return def_val == sec_val
		
def read_config(config_file):
	
	group_runners = []
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	
	def parse_items(context, config, section=ConfigParser.DEFAULTSECT):
		for k, v in config.items(section):
			if k.endswith('_env'):
				k = k[:-4]
				v = os.environ.get(v)
				
			if k.endswith('_args'):
				v = eval(v)
				k = k[:-5]
			setattr(context, k, v)
	
	context = Context()
	parse_items(context, config)
	
	context.serialize = get_bool_option(config, name="serialize")
	context.output_dir = get_option(config, name="output_dir", default='/tmp')
	context.test_name = get_option(config, name="test_name", default='unknown-%s' % time.time())
	
	def noop(*args, **kwargs): pass
	context.setup = resolve(context.setup) if  hasattr(context, "setup") else noop 
	context.teardown = resolve(context.teardown) if  hasattr(context, "teardown") else noop 
	
	# read running groups
	
	context.run_time = get_int_option(config, name="run_time")
	context.rampup = get_int_option(config, name="rampup", default=0)
	context.use_threads = get_bool_option(config, name="use_threads")
	context.call_wait_time = get_float_option(config, name="call_wait_time", default=0)
	context.max_iterations = get_int_option(config, name="max_iterations")
	
	for section in config.sections():
		
		delegate = DelegateContext(context)
		parse_items(delegate, config, section)
		
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
		delegate.target = config.get(section, 'target')
		delegate.target_args = get_option(config, section, 'target_args', None)
		
		delegate.use_threads = get_bool_option(config, section, "use_threads", context.use_threads)
		delegate.call_wait_time = get_float_option(config, section, "call_wait_time", context.call_wait_time)
		
		# get target and params
		delegate.target = resolve(delegate.target)
		delegate.target_args = eval(delegate.target_args) if delegate.target_args else ()
		
		# save the context
		delegate.target.__context__ = delegate
		
		runner = RunnerGroup(group_name = delegate.group_name,
							 run_time = delegate.run_time,
							 max_iterations = delegate.max_iterations,
							 target = delegate.target,
							 target_args = delegate.target_args,
							 num_runners = delegate.runners,
							 rampup = delegate.rampup,
							 use_threads = delegate.use_threads,
							 call_wait_time = delegate.call_wait_time)
		
		runner.__context__ = delegate
		
		group_runners.append(runner)
	
	
	return (context, group_runners)
