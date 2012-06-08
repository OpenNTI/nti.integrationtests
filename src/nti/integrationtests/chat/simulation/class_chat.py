import time
import random
import threading
import multiprocessing

from nti.integrationtests.chat import phrases
from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import Guest
from nti.integrationtests.chat.objects import run_chat
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.chat.simulation.group_chat import pprint_to_file
from nti.integrationtests.chat.simulation import create_test_friends_lists
	
class Moderator(Host):

	def __init__(self, *args, **kwargs):
		super(Moderator, self).__init__(*args, **kwargs)
		self.approval_percentage = 0.3
		
	def chat_recvMessageForModeration(self, **kwargs):
		super(Moderator, self).chat_recvMessageForModeration(**kwargs)
		self.heart_beats = 0
		mid = kwargs['ID']
		if random.random() <= self.approval_percentage:
			self.approveMessages(mid)
			self.moderated_messages.pop(mid , None)
			
	def wait_4_room(self):
		super(Moderator, self).wait_4_room()
		self.makeModerated(self.room)	
		
	def __call__(self, *arg, **kwargs):
		entries = kwargs.get('entries', 50)
		inReplyTo = kwargs.get("inReplyTo", None)
		references = kwargs.get("references", None)
		containerId = kwargs.get('containerId', None)
		max_heart_beats = kwargs.get('max_heart_beats', 2)
		
		max_delay = kwargs.get('max_delay', 45)
		min_delay = kwargs.get('min_delay', 15)
		self.approval_percentage =  kwargs.get('approval_percentage', self.approval_percentage)
		
		exit_event = kwargs.pop('exit_event')
		connect_event = kwargs.pop('connect_event')
		try:
			self.ws_connect()

			self.wait_for_guests_to_connect(max_heart_beats)
			
			self.enterRoom( occupants=self.occupants, containerId=containerId,
							inReplyTo=inReplyTo, references=references)
			self.wait_4_room()
			connect_event.set()
			connect_event.clear()
			
			try:
				room_id = self.room
				if room_id:
					self.post_messages(room_id, entries, connect_event, min_delay, max_delay)
				else:
					raise Exception('%s did not enter a chat room' % self.username)
			finally:
				exit_event.set()

			# process messages
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			out_dir = kwargs.pop('out_dir', None)
			pprint_to_file(self, out_dir=out_dir, **kwargs)
			
	def post_messages(self, room_id, entries, post_event, min_delay=15, max_delay=45, phrases=phrases):
		for i in xrange(entries):
			if i == 0: # wait less for the first message
				delay = random.uniform(1,3)
			else:
				delay = random.randint(min_delay, min_delay)
	
			elapsed = 0
			while elapsed < delay:
				time.sleep(1)
				self.nextEvent() # process any message while waiting
				elapsed = elapsed + 1
			
			content = self.generate_message(k=3, phrases=phrases)
			self.chat_postMessage(message=unicode(content), containerId=room_id)
			post_event.set()
			post_event.clear()
			
class Student(Guest):

	def __call__(self, *arg, **kwargs):
		exit_event = kwargs.pop('exit_event')
		connect_event = kwargs.pop('connect_event')
		max_delay = kwargs.get('max_delay', 45) * 2 
		max_heart_beats = kwargs.get('max_heart_beats', 2)
		response_percentage =  kwargs.get('response_percentage', 0.3)
		
		try:
			self.ws_connect()
			connect_event.wait(60)
			
			self.wait_4_room()
			room_id = self.room
			if not room_id:
				raise Exception('%s did not enter a chat room' % self.username)
			
			time.sleep(1)
			while not exit_event.is_set():
				self.nextEvent()
				connect_event.wait(max_delay)
				time.sleep(1)
				if random.random() <= response_percentage:
					content = self.generate_message(k=3, phrases=phrases)
					self.chat_postMessage(message=unicode(content), containerId=room_id)
				
			# get any message
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			outdir = kwargs.pop('outdir', None)
			pprint_to_file(self, outdir=outdir, **kwargs)
			
	
def simulate(users, containerId, entries=None,
			 server='localhost', port=8081, is_secure=False,
			 approval_percentage=0.3, response_percentage=0.4,
			 min_delay=15, max_delay=45, outdir=None,
			 max_heart_beats=3, use_threads=False, create_test_lists=True,
			 start_user=1):
	
	users = max(min(abs(users), MAX_TEST_USERS), 2)
	entries = abs(entries) if entries else 50
			
	if create_test_lists:
		create_test_friends_lists(users, server, port, is_secure,start_user=start_user)
		
	host = 'test.user.%s@nextthought.com' % start_user
	users =['test.user.%s@nextthought.com' % s for s in range(start_user+1, users+start_user)]
	
	exit_event = threading.Event() if use_threads else multiprocessing.Event()
		
	result = run_chat(containerId, host, users, entries=entries, use_threads=use_threads,
					  server=server, port=port, is_secure=is_secure,
					  max_heart_beats=max_heart_beats, host_class=Moderator, invitee_class=Student,
					  min_delay=min_delay, max_delay=max_delay, exit_event=exit_event, outdir=outdir,
					  approval_percentage=approval_percentage, response_percentage=response_percentage)
	
	return result


