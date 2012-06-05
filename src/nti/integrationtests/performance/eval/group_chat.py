import os
import uuid
import random

from nti.integrationtests.chat.simulation.group_chat import simulate

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def chat(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']
	
	port =  context.as_int( "port", 8081)
	server =  getattr(context, "server", 'localhost')
	is_secure = bool(getattr(context, "is_secure", False))
	
	use_procs =  getattr(context, "use_procs", 'False')
	use_threads = use_procs.lower() == 'false'
	
	min_delay = context.as_int( "min_delay", 15)
	max_delay = context.as_int( "max_delay", 45)
	entries = context.as_int( "entries", 10)
	
	min_users = context.as_int( "min_users", 2)
	max_users = context.as_int( "max_users", 10)
	users = random.randint(min_users, max_users)
	containerId = getattr(context, "containerId",  str(uuid.uuid4()))
	
	result = simulate(	users=users, containerId=containerId, entries=entries,
			 			min_delay=min_delay, max_delay=max_delay,
			 			server=server, port=port, use_threads=use_threads, is_secure=is_secure)
	
	# gather results
	items = []
	for r in result:
		trb = r.traceback.replace('\n','') if r.traceback else ''
		d = {'username': r.username, 
			 'sent': len(list(r.sent)),
			 'recv': len(list(r.received)),
			 'elapsed_recv': r.elapsed_recv,
			 'traceback' : trb}
		items.append(d)
		
	# pretty print results 
	d = {runner : items,'containerId': containerId }
	result = str(d)
	return result

def _set_logger():
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s')
	
def main():
	from nti.integrationtests.performance.runner import run
	_set_logger()
	config_file = os.path.join(os.path.dirname(__file__), "group_chat.cfg")
	run(config_file)
	
if __name__ == '__main__':
	main()
