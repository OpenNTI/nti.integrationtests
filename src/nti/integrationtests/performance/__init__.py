import time
import threading
import multiprocessing

class RunnerGroup(multiprocessing.Process):
	def __init__(self, run_time, num_runners, target, target_args=(), rampup=0, call_wait_time=None,
				 queue=None, group_name=None, start_time=None, use_threads=False, *args, **kwargs):
		super(RunnerGroup, self).__init__(*args, **kwargs)
		self.queue = queue
		self.rampup = rampup
		self.target = target
		self.run_time = run_time
		self.start_time = start_time
		self.num_runners = num_runners
		self.target_args = target_args
		self.use_threads = use_threads
		self.group_name = group_name or ''
		self.call_wait_time = call_wait_time
		
	def __str__(self):
		return self.group_name
	
	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.num_runners, self.run_time, self.ramup)
	
	def run(self):
		runners = []
		for i in xrange(self.num_runners):
			spacing = float(self.rampup) / float(self.num_runners)
			if i > 0:
				time.sleep(spacing)
				
			target = TargetRunner(	runner_num=i, run_time=self.run_time, target=self.target,
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
		while elapsed < self.run_time:
			result = None
			exception = None
			start = time.time()
			try:
				result = self.target(*self.target_args)
			except Exception, e:
				exception = e
		
			run_time = time.time() - start
			
			if self.call_wait_time:
				time.sleep(self.call_wait_time)
			
			elapsed = time.time() - self.start_time
			
			if self.queue:
				self.queue.put(RunnerResult(self.runner_num, run_time, result, exception, self.group_name))
				
class RunnerResult(object):
	def __init__(self, runner_num, run_time, result, exception=None, group_name=None):
		self.result = result
		self.run_time = run_time
		self.exception = exception
		self.runner_num = runner_num
		self.group_name = group_name or ''
		self.epoch = time.mktime(time.localtime())
	
	@classmethod
	def sort(self, array):
		def sorting(x):
			s = '%s-%03d' % (x.group_name, x.runner_num)
			return s.lower()
		return sorted(array, key=sorting)
			
