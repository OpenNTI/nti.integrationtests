from __future__ import print_function, unicode_literals

import os
import six
import time
import numbers

from nti.integrationtests.chat import generate_message
#from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.performance import TimerResultMixin 
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import init_server
from nti.integrationtests.performance.eval import stop_server
from nti.integrationtests.performance.eval import generate_ntiid


from nti.integrationtests.performance.eval import generate_random_text

import logging
logger = logging.getLogger(__name__)
	
# -----------------------------------

def script_setup(context):
	server = context.as_str("server", None)
	if not server:
		init_server(context)
	
def script_teardown(context):
	server = context.as_str("server", None)
	if not server:
		stop_server(context)
	
# -----------------------------------

_max_users = 2000


def _users_loop(users):
	for no in users:
		if isinstance(no, numbers.Integral):
			no = min(no, _max_users-1) 
			sw = ['test.user.%s@nextthought.com' % x for x in range(2, no+2)]
		elif isinstance(no, six.string_types):
			sw = [no]
		else:
			continue
		yield no, sw
		
def create_share(users, *args, **kwargs):
	context = kwargs['__context__']
	client = new_client(context)
	result = TimerResultMixin()
	
	for t in _users_loop(users):
		no, sw = t
		
		# create note
		nttype = generate_random_text()
		message = generate_message(k=3)
		container = generate_ntiid(nttype=nttype)
		now = time.time()
		note = client.create_note(message, container=container, sharedWith=sw)
		elpased = time.time() - now
		assert note, 'could  not create note'
		
		# record time
		result['sop.%s' % no] = elpased
		
	return result

def share_note(users, *args, **kwargs):
	context = kwargs['__context__']
	client = new_client(context)
	runner = kwargs['__runner__']
	
	nttype = generate_random_text()
	container = generate_ntiid(nttype=nttype)
	
	outdir = getattr(context, "result_output_dir", '/tmp')
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	outfile = os.path.join(outdir, str(runner) + ".csv")
	
	with open(outfile,"w") as f:
		users = range(10, 2010, 50) + ['Everyone']
		for t in _users_loop(users):
			message = generate_message(k=3)
			note = client.create_note(message, container=container)
			assert note, 'could  not create note'
			
			no, sw = t
			note['sharedWith'] = sw
			
			# share note
			now = time.time()
			shared_obj = client.update_object(note)
			elpased = time.time() - now
			assert shared_obj, 'could  not share note'
			assert len(shared_obj['sharedWith']) == no, 'did not share w/ all users'
			
			f.write("%s,%s\n" % (no, elpased))
			f.flush()
			
	return None
