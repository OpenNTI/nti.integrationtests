from __future__ import print_function, unicode_literals

import os
import uuid
import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.chat.simulation.group_chat import simulate

import logging
logger = logging.getLogger(__name__)

_max_users = MAX_TEST_USERS

def chat(*args, **kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']
	
	port =  context.as_int( "port", 8081)
	server =  context.as_str("server", 'localhost')
	is_secure = context.as_bool("is_secure", False)
	
	use_procs =  context.as_bool("use_procs", False)
	use_threads = not use_procs
	
	min_delay = context.as_int( "min_delay", 15)
	max_delay = context.as_int( "max_delay", 45)
	entries = context.as_int( "entries", 10)
	
	min_users = context.as_int( "min_users", 2)
	max_users = context.as_int( "max_users", 10)
	users = min(random.randint(min_users, max_users), _max_users)
	containerId = getattr(context, "containerId",  str(uuid.uuid4()))
	
	start_user = (int(runner)-1) * users + 1
	if start_user + users > _max_users:
		start_user = start_user + users - _max_users
	start_user  = max(1, start_user)
	
	outdir = getattr(context, "result_output_dir", '/tmp')
	outdir = os.path.join(outdir, str(runner))
	if not os.path.exists(outdir):
		os.makedirs(outdir)
		
	simulate(users=users, containerId=containerId, entries=entries,
	 		 min_delay=min_delay, max_delay=max_delay,
			 server=server, port=port, use_threads=use_threads, is_secure=is_secure,
			 start_user=start_user, outdir=outdir)
	
	return IGNORE_RESULT

