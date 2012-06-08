import os
import sys
import time
import pprint
import random

from nti.integrationtests.chat import phrases
from nti.integrationtests.chat.objects import run_chat
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.chat.objects import Host as _Host
from nti.integrationtests.chat.objects import Guest as _Guest
from nti.integrationtests.chat.simulation import create_test_friends_lists

def pprint_to_file(self, outdir=None, **kwargs):
	outdir = os.path.expanduser(outdir or '/tmp')
	outname = os.path.join(outdir, self.username + ".txt")
	with open(outname, "w") as s:
		pprint_graph(self, stream=s, **kwargs)
	
def pprint_graph(self, lock=None, stream=None, **kwargs):
	stream = stream or sys.stderr
	try:
		if lock: lock.acquire()
		
		d = {'username' : self.username,
			 'sent' : len(list(self.sent)),
			 'received': len(list(self.received)),
			 'moderated': len(list(self.moderated)),
			 'elapsed_recv': self.elapsed_recv,
			 'traceback': self.traceback,
			 'params' : kwargs }
			
		pprint.pprint(d, stream=stream, indent=2)
	finally:
		if lock: lock.release()
	
def post_messages(self, room_id, entries, min_delay=15, max_delay=45, phrases=phrases):
	for i in xrange(entries):
		if i == 0: # wait less for the first message
			delay = random.uniform(1,5)
		else:
			delay = random.randint(min_delay, min_delay)
	
		elapsed = 0
		while elapsed < delay:
			time.sleep(1)
			self.nextEvent() # process any message while waiting
			elapsed = elapsed + 1
		
		content = self.generate_message(k=3, phrases=phrases)
		self.chat_postMessage(message=unicode(content), containerId=room_id)
		
class Host(_Host):

	def __call__(self, *arg, **kwargs):
		entries = kwargs.get('entries', 50)
		max_delay = kwargs.get('max_delay', 45)
		min_delay = kwargs.get('min_delay', 15)
		inReplyTo = kwargs.get("inReplyTo", None)
		references = kwargs.get("references", None)
		containerId = kwargs.get('containerId', None)
		connect_event = kwargs.get('connect_event', None)
		max_heart_beats = kwargs.get('max_heart_beats', 3)
		
		try:
			self.ws_connect()

			self.wait_for_guests_to_connect(max_heart_beats)
			
			self.enterRoom( occupants=self.occupants, containerId=containerId,
							inReplyTo=inReplyTo, references=references)
			self.wait_4_room()
			connect_event.set()

			# start pos
			room_id = self.room
			if room_id:
				post_messages(self, room_id, entries, min_delay, max_delay)
			else:
				raise Exception('%s did not enter a chat room' % self.username)

			# process messages
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			outdir = kwargs.pop('outdir', None)
			pprint_to_file(self, outdir=outdir, **kwargs)
			
class Guest(_Guest):
	
	def __call__(self, *arg, **kwargs):
		entries = kwargs.get('entries', 50)
		max_delay = kwargs.get('max_delay', 45)
		min_delay = kwargs.get('min_delay', 15)
		max_heart_beats = kwargs.get('max_heart_beats', 3)

		try:
			self.ws_connect()
			event = kwargs.get('connect_event', None)
			event.wait(60)

			self.wait_4_room()

			# write any messages
			room_id = self.room
			if room_id:
				post_messages(self, room_id, entries, min_delay, max_delay)
			else:
				raise Exception('%s did not enter a chat room' % self.username)

			# get any message
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			outdir = kwargs.pop('outdir', None)
			pprint_to_file(self, outdir=outdir, **kwargs)
			
def simulate(users, containerId, entries=None, min_delay=15, max_delay=45, outdir=None,
			 server='localhost', port=8081,
			 max_heart_beats=3, use_threads=True, create_test_lists=True, is_secure=False,
			 start_user=1):
	
	users = max(min(abs(users), MAX_TEST_USERS), 2)
	entries = abs(entries) if entries else 50
			
	if create_test_lists:
		create_test_friends_lists(users, server, port, is_secure,start_user=start_user)
		
	host = 'test.user.%s@nextthought.com' % start_user
	users =['test.user.%s@nextthought.com' % s for s in range(start_user+1, users+start_user)]
	
	if outdir and not os.path.exists(outdir):
		os.makedirs(outdir)
		
	result = run_chat(containerId, host, users, entries=entries, use_threads=use_threads,
					  server=server, port=port, is_secure=is_secure, 
					  max_heart_beats=max_heart_beats, host_class=Host, invitee_class=Guest, 
					  min_delay=min_delay, max_delay=max_delay, outdir=outdir)
	
	return result
