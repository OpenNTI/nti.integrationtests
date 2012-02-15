import time
import inspect
import threading
import multiprocessing

class RunnerGroup(multiprocessing.Process):
	def __init__(self, run_time, num_runners, target, target_args=(), rampup=0, call_wait_time=None,
				 queue=None, group_name=None, start_time=None, use_threads=False, *args, **kwargs):
		
		super(RunnerGroup, self).__init__(*args, **kwargs)
		
		assert run_time > 0, "must specify a valid run time in secs"
		assert num_runners > 0, "must specify a valid number of runners"
		assert inspect.isfunction(target) or callable(target), "must specify a valid target"
		assert tuple(target_args or ()),  "must specify a valid target arguments"
		assert group_name,  "must specify a valid runner group name"
		
		self.queue = queue
		self.rampup = rampup
		self._target = target
		self.run_time = run_time
		self.group_name = group_name
		self.start_time = start_time
		self.num_runners = num_runners
		self.use_threads = use_threads
		self.target_args = target_args or ()
		self.call_wait_time = call_wait_time
		
	def __str__(self):
		return self.group_name
	
	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.num_runners, self.run_time, self.rampup)
	
	def run(self):
		runners = []
		for i in xrange(self.num_runners):
			spacing = float(self.rampup) / float(self.num_runners)
			if i > 0 and spacing:
				time.sleep(spacing)
				
			target = TargetRunner(	runner_num=i, run_time=self.run_time, target=self._target,
									target_args=self.target_args, queue=self.queue, 
									group_name=self.group_name, start_time=self.start_time)
			
			if self.use_threads:
				runner = threading.Thread(target=target, args=())
			else:
				runner = multiprocessing.Process(target=target, args=())
			
			runners.append(runner)
			runner.start()
			
		for runner in runners:
			runner.join()

# ==================

class TargetRunner(object):
	def __init__(self, runner_num, run_time, target, target_args=(), queue=None, 
				 group_name=None, start_time=None, call_wait_time=None):
		self.queue = queue
		self.target = target
		self.exception = None
		self.run_time = run_time
		self.group_name = group_name
		self.runner_num = runner_num
		self.target_args = target_args
		self.call_wait_time = call_wait_time
		self.start_time = start_time or time.time()
		
	def __str__(self):
		return "(%s, %s)" % (self.group_name, self.runner_num)
	
	def __repr__(self):
		return self.__str__()
	
	def __call__(self,  *args, **kwargs):
		self.run()
		
	def run(self):
		elapsed = 0
		iterations = 0
		while elapsed < self.run_time:
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
			
			elapsed = time.time() - self.start_time
			
			if self.queue:
				self.queue.put(RunnerResult(group_name = self.group_name,
											runner_num = self.runner_num, 
											run_time = run_time,
											elapsed = elapsed,
											iteration = iterations,
											result = result,
											exception = exception))
				
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
			
