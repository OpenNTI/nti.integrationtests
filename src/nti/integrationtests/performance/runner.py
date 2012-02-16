import os
import time
import Queue
import shutil
import threading
import multiprocessing

from nti.integrationtests.performance.config import read_config

class ResultsWriter(threading.Thread):
	def __init__(self, queue, output_file):
		super(ResultsWriter, self).__init__(name="resultwriter")
		self.queue = queue
		self.output_file = output_file
			
	def run(self):
		counter = 0
		with open(self.output_file, 'w') as f:
			f.write("counter,group_name,iteration,epoch,target_run_time,elapsed,error,output\n")
			while True:
				try:
					result = self.queue.get_nowait()
					if not result:
						break
					
					counter = counter + 1
					f.write('%i,%s,%i,%i,%f,%.3f,%s,%s\n' % (counter, 
												 			 result.group_name,
												 			 result.iteration,
												 			 result.epoch,	
												 			 result.run_time,
															 result.elapsed, 
															 result.error,
															 result.output))
					
					f.flush()
				except Queue.Empty:
					time.sleep(.05)
					pass

def run(config_file):
		
	context, groups = read_config (config_file)
	
	run_localtime = time.localtime()
	output_dir = os.path.expanduser(context.output_dir)
	
	base_output_dir = os.path.join(output_dir, context.test_name)
	result_output_dir = os.path.join(base_output_dir, time.strftime('%Y.%m.%d_%H.%M.%S', run_localtime))
	if not os.path.exists(result_output_dir):
		os.makedirs(result_output_dir)
	output_file = os.path.join(result_output_dir, 'results.csv')

	queue = multiprocessing.Queue()
	writer = ResultsWriter(queue, output_file)
	writer.daemon = True
	writer.start()
		
	context.setup(context=context)
	try:
		now = time.time()
		
		for group in groups:
			group.queue = queue
			if not context.serialize:
				group.start()
			else:
				group.run()
			
		if not context.serialize:
			for group in groups:
				group.join()
		
		result = time.time() - now
			
		copy_cfg_file = os.path.join(result_output_dir, os.path.basename(config_file))
		shutil.copy(config_file, copy_cfg_file)
		
		return result
	finally:
		time.sleep(2)
		queue.put_nowait(None)
		context.teardown(context=context)
	