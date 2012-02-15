import os
import time
import Queue
import threading
import multiprocessing

from nti.integrationtests.performance.config import read_config

class ResultsWriter(threading.Thread):
	def __init__(self, queue, output_file):
		super(ResultsWriter, self).__init__()
		self.queue = queue
		self.output_file = output_file
			
	def run(self):
		counter = 0
		with open(self.output_file, 'w') as f:
			while True:
				try:
					result = self.queue.get_nowait(False)
					if not result:
						break
					
					counter = counter + 1
					f.write('%i,%.3f,%i,%s,%f,%s,%s\n' % (counter, 
														  result.elapsed, 
														  result.epoch,
														  result.group_name,
														  result.run_time,
														  result.error,
														  result.output))
					f.flush()
				except Queue.Empty:
					time.sleep(.05)
					pass

def run_groups(context, groups):
		
	run_localtime = time.localtime()
	output_dir = os.path.expanduser(context.output_dir)
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
			
	name = '%s_%s.csv' % (context.test_name, time.strftime('%Y.%m.%d_%H.%M.%S/', run_localtime))
	output_file = os.path.join(output_dir, name)
	
	queue = multiprocessing.Queue()
	writer = ResultsWriter(queue, output_file)
	writer.daemon = True
	writer.start()
	
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
		
		return time.time() - now
	finally:
		time.sleep(2)
		queue.put_nowait(None)
		
def run(config_file):
	context, groups = read_config (config_file)
	return run_groups(context, groups)

	