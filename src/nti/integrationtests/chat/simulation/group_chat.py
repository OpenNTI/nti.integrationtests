import os
import random

from nti.integrationtests.chat.objects import run_chat
from nti.integrationtests.chat.objects import Host as _Host
from nti.integrationtests.chat.objects import Guest as _Guest
from nti.integrationtests.nltk import default_message_generator
from nti.integrationtests.chat.simulation import pprint_to_file
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.chat.simulation import wait_and_process
from nti.integrationtests.chat.simulation import create_test_friends_lists
	
import logging
logger = logging.getLogger(__name__)
	
message_generator = None

def post_messages(self, room_id, entries, min_delay=15, max_delay=45, min_words=10, max_words=40):
	
	min_words = min_words or 10
	max_words = max_words or 40
	
	for i in xrange(entries):
		if i == 0: # wait less for the first message
			delay = random.uniform(1,5)
		else:
			delay = random.uniform(min_delay, min_delay)
	
		wait_and_process(self, delay)		
		content = message_generator.generate(random.randint(min_words, max_words))
		self.chat_postMessage(message=unicode(content), containerId=room_id)
		
		logging.info("message %s was posted from %s" % (i+1, self))
		
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
		min_words = kwargs.get('min_words', 10)
		max_words = kwargs.get('max_words', 40)
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
				post_messages(self, room_id, entries, min_delay, max_delay,
							  min_words=min_words, max_words=max_words)
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
			 start_user=1, min_words=10, max_words=40):
	
	global message_generator
	message_generator = default_message_generator()
	
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
					  min_delay=min_delay, max_delay=max_delay, min_words=min_words, 
					  max_words=max_words, outdir=outdir)
	
	return result
