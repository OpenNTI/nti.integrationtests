import multiprocessing

class RunnerGroup(multiprocessing.Process):
	def __init__(self, run_time, num_runners=1, target, target_args=(), rampup=0, 
				 target_args, queue=None, group_name=None, use_threads=False, *args, **kwargs):
		super(RunnerGroup, self).__init__(*args, **kwargs)
		self.queue = queue
		self.ramup = rampup
		self.target = target
		self.run_time = run_time
		self.num_runners = num_runners
		self.target_args = target_args
		self.group_name = group_name or ''
		
	def __repr__(self):
		return "(%s, %s, %s, %s)" % (self.group_name, self.num_runners, self.run_time, self.ramup)
	
	def run(self):
		runners = []
		for i in xrange(self.num_runners):
			pass
		