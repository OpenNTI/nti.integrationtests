import os
import time
import Queue
import shutil
import threading
import multiprocessing

from nti.integrationtests.performance import Subscriber
from nti.integrationtests.performance import result_headers as headers
from nti.integrationtests.performance.config import read_config
from nti.integrationtests.performance.datastore import ResultDbWriter
from nti.integrationtests.performance.datastore import ResultBatchDbLoader

import logging
logger = logging.getLogger(__name__)

# -----------------------------------

class ResultEventNotifier(threading.Thread):
	def __init__(self, queue, timestamp, groups, subscribers=[]):
		super(ResultEventNotifier, self).__init__(name="ResultEventNotifier")
		self.queue = queue
		self.timestamp = timestamp
		self.subscribers = subscribers
		self.groups = { g.group_name: g for g in groups }
			
	def run(self):
		while True:
			try:
				result = self.queue.get_nowait()
				if result:
					for subscriber in self.subscribers:
						subscriber(self.timestamp, self.groups[result.group_name], result)
				
				self.queue.task_done()
				if not result: break
			except Queue.Empty:
				time.sleep(.05)
			except Exception, e:
				self.queue.task_done()
				logger.error(e)
				

# -----------------------------------

class ResultFileWriter(Subscriber):
	
	def __init__(self, output_file):
		super(ResultFileWriter, self).__init__()
		self.counter = 0
		self.output_file = output_file
		self.formats = '\t'.join(('%i', '%s', '%i', '%i', '%i', '%f', '%.3f', '%s', '%s', '%s'))
		self.stream = self.prepare_stream()
		logger.info("saving results to '%s'", self.output_file)
		
	def prepare_stream(self):
		stream = open(self.output_file, 'w')
		stream.write('\t'.join(headers))
		stream.write('\n')
		return stream
		
	def close(self):
		self.stream.close()
		
	def __call__(self, timestamp, group, result):
		self.counter = self.counter + 1
		self.stream.write(self.formats % (	self.counter, 
											result.group_name,
											result.runner_num,
											result.iteration,
											result.epoch,	
											result.run_time,
											result.elapsed, 
											result.error,
											result.output,
											result.timers_to_string()))
		self.stream.write('\n')
		self.stream.flush()
		
# -----------------------------------

def _call_subscribers_method(subscribers, method_name):
	for s in subscribers:
		method = getattr(s, method_name, None)
		if method:
			try:
				method()
			except Exception, e:
				logger.exception(e)
	
def setup_subscribers(subscribers):
	_call_subscribers_method(subscribers, 'setup')
					
def close_subscribers(subscribers):
	_call_subscribers_method(subscribers, 'close')
	
def close_queue(queue):
	time.sleep(2)
	queue.put_nowait(None)
	queue.join()
	
def run(config_file):
	
	context, groups = read_config (config_file)
	
	run_localtime = time.localtime()
	timestamp = time.strftime('%Y.%m.%d_%H.%M.%S', run_localtime)
	subscribers = []
	
	batch_loader = None
	output_dir = context.output_dir
	if output_dir:
		output_dir = os.path.expanduser(context.output_dir)
		base_output_dir = os.path.join(output_dir, context.test_name)
	
		# set result file
		result_output_dir = os.path.join(base_output_dir, timestamp)
		if not os.path.exists(result_output_dir):
			os.makedirs(result_output_dir)
		output_file = os.path.join(result_output_dir, 'results.txt')

		# add csv data subscriber
		subscribers.append(ResultFileWriter(output_file))
		
		# set database subscriber/loader
		db_file = context.database_file
		if db_file:
			db_path = os.path.join(base_output_dir, db_file)
			if context.db_batch:
				batch_loader = ResultBatchDbLoader(db_path)
			else:
				subscribers.append(ResultDbWriter(db_path))
			
	queue = multiprocessing.JoinableQueue()
	notifier = ResultEventNotifier(queue, timestamp, groups, subscribers)
	notifier.daemon = True
	notifier.start()
		
	context.script_setup(context=context)
	try:
		setup_subscribers(subscribers)
		now = time.time()
		
		for group in groups:
			group.queue = queue
			if not context.serialize:
				group.start()
			else:
				group.run()
			
			# get a hold of results
			context[group.group_name] = group.results
			
		if not context.serialize:
			for group in groups:
				group.join()
		
		result = time.time() - now
			
		copy_cfg_file = os.path.join(result_output_dir, 'results.cfg')
		shutil.copy(config_file, copy_cfg_file)
		
		return result
	finally:
		close_queue(queue)
		close_subscribers(subscribers)
		context.script_teardown(context=context)
		if batch_loader: batch_loader.do_batch_load(output_file, timestamp, groups)
	