import time
import inspect
import numbers
import UserDict
import threading
import multiprocessing

import logging
logger = logging.getLogger(__name__)

# -----------------------------------

read_only_attributes = ('script_setup', 'script_teardown', 'output_dir',
						'database_file', 'db_batch', 'base_path', 'script_subscriber')

default_attributes = (	'rampup', 'run_time','test_name', 'output_dir', 'serialize','use_threads',
						'max_iterations', 'call_wait_time') + read_only_attributes

group_attributes = ('runners', 'target', 'target_args', 'setup', 'teardown')

all_attributes = default_attributes +  group_attributes

result_headers = (	'counter','group_name', 'runner_num', 'iteration', 'epoch', 'run_time', 
					'elapsed','error','output', 'timers')

# -----------------------------------

def noop(*args, **kwargs): pass
IGNORE_RESULT = object()

# -----------------------------------

class DataMixin(object, UserDict.DictMixin):
	def __init__(self, data=None):
		self._data = data if data is not None else {}

	def __contains__( self, key ):
		return key in self._data

	def __getitem__(self, key):
		return self._data[key]

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
	
# -----------------------------------

class TimerResultMixin(DataMixin):
	def __init__(self, data=None, result=None):
		super(TimerResultMixin, self).__init__(data=data)
		self.result = result

	def __getitem__(self, key):
		return self._data[key] if key in self._data else None
	
	def __setitem__(self, key, val):
		assert isinstance(val, numbers.Real)
		super(TimerResultMixin, self).__setitem__(key, val)
		
	@property
	def timers(self):
		return self._data
	
# -----------------------------------

class Context(DataMixin):
	
	manager = multiprocessing.Manager()
	
	def __getitem__(self, key):
		return self._data[key] if key in self._data else None

class DelegateContext(Context):

	def __init__(self, context):
		super(DelegateContext, self).__init__(data=context._data)
		self.__dict__['delegate'] = context
			
	def __getattribute__(self, name):
		if name in read_only_attributes:
			raise AttributeError('Cannot access %s' % name)
		return super(DelegateContext, self).__getattribute__(name)
	
	def __getattr__(self, name):
		return getattr(self.__dict__['delegate'],name)
	
	def __setattr__(self, name, value):
		if name not in read_only_attributes:
			self.__dict__[name] = value
			
	def to_external_object(self):
		external = {}
		for k, v in self.__dict__.items():
			if k.startswith("_"):
				continue
			
			if isinstance(v, numbers.Real) or isinstance(v, basestring):
				external[k] = v
			elif inspect.isfunction(v):
				external[k] = '%s.%s' % (v.__module__, v.__name__)
			elif isinstance(v, (list, tuple, dict)):
				external[k] = repr(v)
				
		return external
			
# -----------------------------------

def validate_context(context):
	
	assert 	isinstance(context, DelegateContext), 'must specify a valid context'
	assert 	context.run_time or context.max_iterations, \
			"must specify a valid run time in secs or max number of iterations"
	
	if context.run_time:
		assert context.run_time > 0, "must specify a valid run time in secs"
			
	if context.max_iterations:
		assert context.max_iterations > 0, "must specify a valid number of max iterations"
			
	assert context.runners > 0, "must specify a valid number of runners"
	assert inspect.isfunction(context.target) or callable(context.target), "must specify a valid target"
		
	if context.target_args:
		assert tuple(context.target_args),  "must specify a valid target arguments"
			
	assert context.group_name,  "must specify a valid runner group name"

# -----------------------------------

class RunnerGroup(multiprocessing.Process):
	def __init__(self, context, queue=None, validate=True, *args, **kwargs):
		super(RunnerGroup, self).__init__(*args, **kwargs)
		if validate: validate_context(context)
		self.context = context
		self.queue = queue
		if self.hold_results: self._results = []
		
	def __str__(self):
		return self.group_name
	
	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.runners, self.run_time, self.rampup)
	
	# ----------------
	
	def _add_result(self, runner):
		if self.hold_results:
			self._results.extend(runner.results)
			
	@property
	def results(self):
		return getattr(self, '_results', [])
	
	@property
	def runners(self):
		return self.context.runners
	
	@property
	def group_name(self):
		return self.context.group_name
	
	@property
	def run_time(self):
		return getattr(self.context, 'run_time', None)
	
	@property
	def rampup(self):
		return getattr(self.context,'rampup', 0)

	@property
	def use_threads(self):
		return getattr(self.context, 'use_threads', False)
		
	@property
	def hold_results(self):
		return getattr(self.context, 'hold_results', False)
			
	@property
	def setup(self):
		return self.context.setup
		
	@property
	def teardown(self):
		return self.context.teardown
	
	def run(self):
		targets = []

		self.setup(self.context)
		logging.info("group '%s' started", self.group_name)
		
		t = time.time()		
		try:
			for i in xrange(self.runners):
				spacing = float(self.rampup) / float(self.runners)
				if i > 0 and spacing:
					time.sleep(spacing)
					
				target = TargetRunner(runner_num=i+1, context=self.context, queue=self.queue)			
				if self.use_threads:
					runner = threading.Thread(target=target, args=())
				else:
					runner = multiprocessing.Process(target=target, args=())
				
				targets.append(runner)
				runner.start()
				
			for runner in targets:
				runner.join()
				self._add_result(runner)
		finally:
			self.teardown(self.context)
			elapsed = time.time() - t
			logging.info("group '%s' completed in (%.3f)s", self.group_name, elapsed)

# -----------------------------------

class TargetRunner(object):
	def __init__(self, runner_num, context, queue=None):
		self.runner_num = runner_num
		self.context = context
		self.queue = queue
		if self.hold_results: self._results = []
		
	def __str__(self):
		return "(%s, %s)" % (self.group_name, self.runner_num)
	
	def __repr__(self):
		return self.__str__()
	
	def __call__(self,  *args, **kwargs):
		self.run()
		
	# ----------------
	
	@property
	def results(self):
		return getattr(self, '_results', [])
	
	@property
	def hold_results(self):
		return getattr(self.context, 'hold_results', False)
	
	@property
	def run_time(self):
		return getattr(self.context, 'run_time', None)
			
	@property
	def max_iterations(self):
		return getattr(self.context, 'max_iterations', None)
	
	@property
	def call_wait_time(self):
		return getattr(self.context, 'call_wait_time', None)
	
	@property
	def start_time(self):
		return getattr(self.context, 'start_time', time.time())
	
	@property
	def target(self):
		return self.context.target
	
	@property
	def target_args(self):
		return self.context.target_args
		
	@property
	def group_name(self):
		return self.context.group_name
	
	@property
	def allow_context(self):
		spec = inspect.getargspec(self.target)
		return (spec.args and spec.args[-1] == '__context__') or spec.keywords
		
	def run(self):
		elapsed = 0
		iterations = 0
		start_time = self.start_time
		
		logging.info("runner '%s' started. Run time=%s, Max iterations=%s", 
					 self.runner_num, self.run_time, self.max_iterations)
		
		can_bind_context = self.allow_context
		while 	(self.run_time and elapsed < self.run_time) or \
				(self.max_iterations and iterations < self.max_iterations):
			
			result = None
			exception = None
			start = time.time()
			try:
				if can_bind_context:
					result = self.target(*self.target_args, __context__=self.context)
				else:
					result = self.target(*self.target_args)
			except Exception, e:
				exception = e
		
			iterations = iterations + 1
			run_time = time.time() - start
			
			if self.call_wait_time:
				time.sleep(self.call_wait_time)
			
			elapsed = time.time() - start_time
			
			if IGNORE_RESULT != result:
				
				if isinstance(result, TimerResultMixin):
					custom_timers = result.timers
					result = result.result
				else:
					custom_timers = None
					
				runner_result = RunnerResult(group_name = self.group_name,
											 runner_num = self.runner_num, 
											 run_time = run_time,
											 elapsed = elapsed,
											 iteration = iterations,
											 result = result,
											 exception = exception,
											 custom_timers = custom_timers)
				
				if self.queue:
					self.queue.put(runner_result)
					
				if self.hold_results:
					self._results.append(runner_result)
			
		logging.info("runner '%s' completed. Time=%s, iterations=%s", self.runner_num, elapsed, iterations)
		
# -----------------------------------
	
class RunnerResult(object):
	
	def __init__(self, group_name, runner_num, run_time, elapsed, iteration, 
				 result=None, exception=None, epoch=None, custom_timers={}):
		self.result = result
		self.elapsed = elapsed
		self.run_time = run_time
		self.exception = exception
		self.iteration = iteration
		self.runner_num = runner_num
		self.group_name = group_name
		self.custom_timers = custom_timers or {}
		self.epoch = epoch or time.mktime(time.localtime())
	
	def __str__(self):
		return self.__repr__()
	
	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.runner_num, self.iteration, self.run_time)
	
	@property
	def error(self):
		return str(self.exception) if self.exception else ''
	
	@property
	def output(self):
		return repr(self.result) if self.result else ''
	
	@property
	def timers(self):
		return self.custom_timers
	
	def timers_to_string(self, delim='\t'):
		lst = ['%s:%f' % (k,v) for k,v in self.custom_timers.iteritems()]
		return delim.join(lst)
	
	def to_external_object(self):
		external = {}
		external['epoch'] = self.epoch
		external['result'] = self.result
		external['elapsed'] = self.elapsed
		external['run_time'] = self.run_time
		external['exception'] = self.exception
		external['iteration'] = self.iteration
		external['runner_num'] = self.runner_num
		external['group_name'] = self.group_name
		external['custom_timers'] = dict(self.custom_timers)
		return external
			
# -----------------------------------

class Subscriber(object):
	
	def setup(self, *args, **kwargs):
		pass
	
	def __call__(self, *args, **kwargs):
		pass

	def close(self, *args, **kwargs):
		pass
