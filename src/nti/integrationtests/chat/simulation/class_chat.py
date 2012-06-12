import os
import time
import random
import threading
import multiprocessing

from nti.integrationtests.chat import phrases
from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import Guest
from nti.integrationtests.chat.objects import run_chat
from nti.integrationtests.chat.simulation import pprint_to_file
from nti.integrationtests.chat.simulation import MAX_TEST_USERS
from nti.integrationtests.chat.simulation import wait_and_process
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
		reply_counter = kwargs.get('reply_counter', None)
		max_heart_beats = kwargs.get('max_heart_beats', 3)
		
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
					self.post_messages(room_id, entries, connect_event, reply_counter, min_delay, max_delay)
				else:
					raise Exception('%s did not enter a chat room' % self.username)
			finally:
				exit_event.set()

			# process any remaning message
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			outdir = kwargs.pop('outdir', None)
			pprint_to_file(self, outdir=outdir, full=True, **kwargs)
			
	def post_messages(self, room_id, entries, post_event, reply_counter,
					  min_delay=15, max_delay=45, phrases=phrases):
		
		post_event.clear()
				
		for i in xrange(entries):
			if i == 0: # wait less for the first message
				delay = random.uniform(1,3)
			else:
				delay = random.randint(min_delay, max_delay)
	
			wait_and_process(self, delay)
			
			# post a question
			content = self.generate_message(k=2, phrases=phrases)
			self.chat_postMessage(message=unicode(content), containerId=room_id)
			
			f = lambda : reply_counter.value < len(self.online)
			wait_and_process(self, max_delay, f)
			reply_counter.value = 0 # reset
			
class Student(Guest):

	def __init__(self, *args, **kwargs):
		super(Student, self).__init__(*args, **kwargs)
		self.moderator = None
		self.reply_counter = 0
		self.response_percentage = 0.3
		
	def chat_recvMessage(self, **kwargs):
		super(Student, self).chat_recvMessage(**kwargs)
		creator = kwargs.get('Creator', kwargs.get('creator', None))
		if creator == self.moderator:
			if random.random() <= self.response_percentage:
				content = self.generate_message(k=2, phrases=phrases)
				self.chat_postMessage(message=unicode(content), containerId=self.room)
			self.reply_counter.value += 1 
		
	def __call__(self, *arg, **kwargs):
		
		self.moderator = kwargs.pop('moderator')
		self.reply_counter = kwargs.pop('reply_counter')
		self.response_percentage =  kwargs.get('response_percentage', 0.3)
		
		exit_event = kwargs.pop('exit_event')
		connect_event = kwargs.pop('connect_event')
		max_heart_beats = kwargs.get('max_heart_beats', 3)
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

			# process any remaning message
			self.wait_heart_beats(max_heart_beats)
			
		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()
			outdir = kwargs.pop('outdir', None)
			pprint_to_file(self, outdir=outdir, full=True, **kwargs)
			
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
	exit_event.clear()
	
	if outdir and not os.path.exists(outdir):
		os.makedirs(outdir)
		
	reply_counter = multiprocessing.Value('i', 0)
	result = run_chat(containerId, host, users, entries=entries, use_threads=use_threads,
					  server=server, port=port, is_secure=is_secure,
					  max_heart_beats=max_heart_beats, host_class=Moderator, invitee_class=Student,
					  min_delay=min_delay, max_delay=max_delay, exit_event=exit_event, outdir=outdir,
					  approval_percentage=approval_percentage, response_percentage=response_percentage,
					  reply_counter=reply_counter, moderator=host)
	
	return result


