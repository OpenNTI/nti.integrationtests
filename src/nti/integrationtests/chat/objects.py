from __future__ import print_function, unicode_literals

import sys
import time
import random
import traceback
import threading
import multiprocessing
from StringIO import StringIO

from nti.integrationtests.utils import generate_message, phrases
from nti.integrationtests.chat import (SOCKET_IO_HOST, SOCKET_IO_PORT)

from nti.integrationtests.chat.socketio_interface import DSUser
from nti.integrationtests.chat.socketio_interface import Serverkill
from nti.integrationtests.chat.socketio_interface import InActiveRoom
from nti.integrationtests.chat.socketio_interface import CouldNotEnterRoom
from nti.integrationtests.chat.socketio_interface import NotEnoughOccupants

class BasicUser(DSUser):
	def __init__(self, *args, **kwargs):
		kwargs['host'] = kwargs.get('host', SOCKET_IO_HOST)
		kwargs['port'] = kwargs.get('port', SOCKET_IO_PORT)
		DSUser.__init__(self, *args, **kwargs)
		self.exception = None
		self.traceback = None

	def __str__(self):
		return self.username if self.username else self.socketio_url

	def __repr__(self):
		return "<%s,%s>" % (self.__class__.__name__,self.__str__())

	def __call__(self, *args, **kwargs):
		pass

	def serverKill(self, args=None):
		super(BasicUser, self).serverKill(args)
		raise Serverkill(args)

	def wait_heart_beats(self, max_beats=3, tick=3):
		counter = 0
		self.heart_beats = 0
		while self.heart_beats < max_beats:
			counter +=1 
			self.nextEvent()
			if counter % tick == 0:
				self.send_heartbeat()

	@property
	def first_room(self):
		return self.rooms.keys()[0] if len(self.rooms) > 0 else None

	def generate_message(self, k=4, phrases=phrases):
		return generate_message(k=4, phrases=phrases)
			
	def post_random_messages(self, room_id, entries=None, a_min=3, a_max=10, delay=None, tick=5):
		counter = 0
		entries = entries or random.randint(a_min, a_max)
		for _ in xrange(entries):
			counter += 1
			content = self.generate_message()
			self.chat_postMessage(message=unicode(content), containerId=room_id)
			if delay is not None and delay > 0:
				time.sleep(delay)
			if counter % tick == 0:
				self.send_heartbeat()

	def save_traceback(self, e=None):
		sio = StringIO()
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback, file=sio)
		sio.seek(0)
		self.exception = e
		self.traceback = sio.read()

class OneRoomUser(BasicUser):

	def __init__(self, *args, **kwargs):
		super(OneRoomUser, self).__init__(*args, **kwargs)
		self.last_post_time = None
		self.last_recv_time = None
		self.creation_time = time.time()

	# ======================

	def chat_enteredRoom(self, **kwargs):
		super(OneRoomUser, self).chat_enteredRoom(**kwargs)
		rid = self.room
		if not rid:
			if not kwargs['active']:
				raise InActiveRoom(rid)
			else:
				occupants = kwargs.get('occupants', [])
				if len(occupants) <= 1:
					raise NotEnoughOccupants(rid)

	def chat_postMessage(self, **kwargs):
		super(OneRoomUser, self).chat_postMessage(**kwargs)
		self.last_post_time = time.time()

	def chat_recvMessage(self, **kwargs):
		message = super(OneRoomUser, self).chat_recvMessage(**kwargs)
		creator = kwargs.get('Creator',  kwargs.get('creator', None))
		cid = kwargs.get('ContainerId',  kwargs.get('containerId', None))
		if cid == self.room and creator != self.username:
			self.heart_beats = 0
		else:
			self.recv_messages.pop(kwargs['ID'] , None)
		self.last_recv_time = time.time()
		return message

	def wait_4_room(self, max_beats=5, tick=3):
		counter = 0
		self.heart_beats = 0
		while self.heart_beats < max_beats and not self.room:
			counter += 1
			self.nextEvent()
			if counter % tick == 0:
				self.send_heartbeat()

		if self.heart_beats >= max_beats and not self.room:
			raise CouldNotEnterRoom()

	# ======================

	def post_messages(self, room_id, entries, delay=0.25, min_phrases=5):
		self.post_random_messages(room_id, entries, min_phrases, delay=delay)

	# ======================

	@property
	def room(self):
		return self.first_room

	@property
	def elapsed_recv(self):
		return self.last_recv_time - self.creation_time if self.last_recv_time else None

	@property
	def elapsed_post(self):
		return self.last_post_time - self.creation_time if self.last_post_time else None

class Host(OneRoomUser):

	def __init__(self, username, occupants, membership=None, *args, **kwargs):
		super(Host, self).__init__(username=username, **kwargs)
		self.online = set()
		self.occupants = occupants
		self.membership = (membership,) if membership else occupants

	@property
	def users_online(self):
		return list(sorted(self.online))

	def chat_presenceOfUserChangedTo(self, username, status):
		if status == 'Online' and username in self.occupants:
			self.online.add(username)
			self.heart_beats = 0

	def wait_for_guests_to_connect(self, max_heart_beats=3, tick=3):
		counter = 0 
		self.heart_beats = 0
		while self.heart_beats < max_heart_beats and len(self.online) < len(self.occupants):
			self.nextEvent()
			counter = counter + 1
			if counter % tick == 0:
				self.send_heartbeat()
			
	def __call__(self, *arg, **kwargs):

		delay = kwargs.get('delay', 0.05)
		entries = kwargs.get('entries', None)
		inReplyTo = kwargs.get("inReplyTo", None)
		references = kwargs.get("references", None)
		containerId = kwargs.get('containerId', None)
		connect_event = kwargs.get('connect_event', None)
		max_heart_beats = kwargs.get('max_heart_beats', 2)

		try:
			self.ws_connect()

			self.wait_for_guests_to_connect(max_heart_beats)

			self.enterRoom(	occupants=self.membership, containerId=containerId,
							inReplyTo=inReplyTo, references=references)
			self.wait_4_room()
			connect_event.set()

			room_id = self.room
			if room_id:
				self.post_messages(room_id, entries, delay=delay)
			else:
				raise Exception('%s did not enter a chat room' % self.username)

			# process messages
			self.wait_heart_beats(max_heart_beats)

		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()

class Guest(OneRoomUser):

	def __call__(self, *args, **kwargs):
		try:
			delay = kwargs.get('delay', 0.05)
			entries = kwargs.get('entries', None)
			max_heart_beats = kwargs.get('max_heart_beats', 2)

			# connect
			self.ws_connect()

			# check for an connect event
			event = kwargs.get('connect_event', None)
			event.wait(20)

			self.wait_4_room()

			# write any messages
			room_id = self.room
			if room_id:
				self.post_messages(room_id, entries, delay=delay)
			else:
				raise Exception('%s did not enter a chat room' % self.username)

			# get any message
			self.wait_heart_beats(max_heart_beats)

		except Exception, e:
			self.save_traceback(e)
		finally:
			self.ws_capture_and_close()

User = Guest
Invitee = Guest

def run_chat(containerId, host_user, invitees, entries=None, delay=0.05,
			 max_heart_beats=2, use_threads=True, host_class=Host, invitee_class=Invitee,
			 server=SOCKET_IO_HOST, port=SOCKET_IO_PORT, is_secure=False,
			 occupants=None, **kwargs):

	runnables = []
	entries = entries or random.randint(5, 20)
	connect_event = threading.Event() if use_threads else multiprocessing.Event()

	occupants = occupants or invitees
	host = host_class(host_user, occupants, host=server, port=port, is_secure=is_secure)
	users = [invitee_class(username=name, host=server, port=port, is_secure=is_secure) for name in invitees]

	required_args = {'entries':entries, 'containerId':containerId, 'connect_event':connect_event,
					 'max_heart_beats':max_heart_beats}

	required_args['delay'] = kwargs.get('delay', delay)

	runnable_args = dict(kwargs)
	runnable_args.update(required_args)

	# start host
	runnable = 	threading.Thread(target=host, kwargs=dict(runnable_args)) if use_threads else \
		 		multiprocessing.Process(target=host, kwargs=dict(runnable_args))
	runnable.start()
	runnables.append(runnable)

	# wait for host to connect
	time.sleep(1)

	# start users
	for u in users:
		runnable = 	threading.Thread(target=u, kwargs=dict(runnable_args)) if use_threads else \
		 			multiprocessing.Process(target=u, kwargs=dict(runnable_args))
		runnable.start()
		runnables.append(runnable)

	# wait for termination
	for t in runnables:
		t.join()

	result = [host]
	result.extend(users)

	return result
