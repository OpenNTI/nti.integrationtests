import os

from nti.integrationtests.performance import RunnerResult
from nti.integrationtests.performance.config import read_config

def process_record(line):
	tokens = line.split('\t') if line else []
	if len(tokens) < 9: return None
	try:
		timers = {}
		for s in tokens[9:]:
			splits = s.split(":")
			timers[splits[0]] = float(splits[1])
		
		record = RunnerResult(group_name = tokens[1],
							  runner_num = int(tokens[2]),
							  iteration = int(tokens[3]),
							  epoch = int(tokens[4]),
							  run_time = float(tokens[5]),
							  elapsed = float(tokens[6]),
							  exception = tokens[7],
							  result = tokens[8],
							  custom_timers = timers)
		
		return record
	except:
		return None
			
def load_results(result_file, on_record=None):
	records = []
	with open(result_file, "r") as f:
		counter = 0
		in_record=False
		for line in f.readlines():
			line = line.rstrip()
			if in_record:
				record = process_record(line)
				if record:
					counter = counter + 1
					if on_record:
						on_record(record)
					else:
						records.append(record)
			in_record=True
	return records

def read_config_and_results(path):
	path = os.path.expanduser(path)
	results_file = os.path.join(path, 'results.txt')
	config_file = os.path.join(path, 'results.cfg')
	
	load_results(results_file)
	context, groups = read_config(config_file, False)
	
	return context, groups

if __name__ == '__main__':
	read_config_and_results('/Users/csanchez/Downloads/test')