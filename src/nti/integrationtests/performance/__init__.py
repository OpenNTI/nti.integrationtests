import time
import inspect
import UserDict
import threading
import multiprocessing

# ====================

read_only_attributes = ('script_setup', 'script_teardown')

default_attributes = ('rampup', 'run_time','test_name', 'output_dir', 'serialize','use_threads',
					'max_iterations', 'call_wait_time') + read_only_attributes

group_attributes = ('runners', 'target', 'target_args', 'setup', 'teardown')

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
			
#  ----------------------

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

# ==================

class RunnerGroup(multiprocessing.Process):
	def __init__(self, context, queue=None, *args, **kwargs):
		super(RunnerGroup, self).__init__(*args, **kwargs)
		validate_context(context)
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
		try:
			for i in xrange(self.runners):
				spacing = float(self.rampup) / float(self.runners)
				if i > 0 and spacing:
					time.sleep(spacing)
					
				target = TargetRunner(runner_num=i, context=self.context, queue=self.queue)			
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

# ==================

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
						
	def run(self):
		elapsed = 0
		iterations = 0
		start_time = self.start_time
		
		while 	(self.run_time and elapsed < self.run_time) or \
				(self.max_iterations and iterations < self.max_iterations):
			
			result = None
			exception = None
			start = time.time()
			try:
				result = self.target(*self.target_args)
			except Exception, e:
				exception = e
		
			iterations = iterations + 1
			run_time = time.time() - start
			
			if self.call_wait_time:
				time.sleep(self.call_wait_time)
			
			elapsed = time.time() - start_time
			
			runner_result = RunnerResult(group_name = self.group_name,
										 runner_num = self.runner_num, 
										 run_time = run_time,
										 elapsed = elapsed,
										 iteration = iterations,
										 result = result,
										 exception = exception)
			if self.queue:
				self.queue.put(runner_result)
				
			if self.hold_results:
				self._results.append(runner_result)
			
# ==================
	
class RunnerResult(object):
	def __init__(self, group_name, runner_num, run_time, elapsed, iteration, result=None, exception=None):
		self.result = result
		self.elapsed = elapsed
		self.run_time = run_time
		self.exception = exception
		self.iteration = iteration
		self.runner_num = runner_num
		self.group_name = group_name
		self.epoch = time.mktime(time.localtime())
	
	def key(self):
		return "%s-%s" % (self.runner_num, self.iteration)
	
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
	
	@classmethod
	def sort(self, array):
		def sorting(x):
			s = '%s-%03d' % (x.group_name, x.runner_num)
			return s.lower()
		return sorted(array, key=sorting)
			
