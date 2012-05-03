import sys
import time
import random
import traceback
import threading
import multiprocessing
from StringIO import StringIO

from nti.integrationtests.chat import generate_message
from nti.integrationtests.chat import (SOCKET_IO_HOST, SOCKET_IO_PORT)

from nti.integrationtests.chat.websocket_interface import Graph
from nti.integrationtests.chat.websocket_interface import Serverkill
from nti.integrationtests.chat.websocket_interface import InActiveRoom
from nti.integrationtests.chat.websocket_interface import CouldNotEnterRoom
from nti.integrationtests.chat.websocket_interface import NotEnoughOccupants

# ----------------------------

class BasicUser(Graph):
	def __init__(self, *args, **kwargs):
		kwargs['host'] = kwargs.get('host', SOCKET_IO_HOST)
		kwargs['port'] = kwargs.get('port', SOCKET_IO_PORT)
		Graph.__init__(self, *args, **kwargs)
		self.exception = None
		self.traceback = None

	def __str__(self):
		return self.username if self.username else self.socketio_url

	def __repr__(self):
		return "<%s,%s>" % (self.__class__.__name__,self.__str__())


	def __call__(self, *args, **kwargs):
		pass

	# ======================

	def serverKill(self, args=None):
		super(BasicUser, self).serverKill(args)
		raise Serverkill(args)

	def wait_heart_beats(self, max_beats=3):
		self.heart_beats = 0
		while self.heart_beats < max_beats:
			self.nextEvent()

	# ======================

	@property
	def first_room(self):
		return self.rooms.keys()[0] if len(self.rooms) > 0 else None

	# ======================

	def generate_message(self, aMin=1, aMax=4):
		return generate_message(aMin, aMax)

	def post_random_messages(self, room_id, entries=None, a_min=3, a_max=10, delay=None):
		entries = entries or random.randint(a_min, a_max)
		for _ in xrange(entries):
			content = self.generate_message()
			self.chat_postMessage(message=unicode(content), containerId=room_id)
			if delay is not None and delay > 0:
				time.sleep(delay)

# ----------------------------

class OneRoomUser(BasicUser):

	def __init__(self, *args, **kwargs):
		super(OneRoomUser, self).__init__(*args, **kwargs)
		self._room = None

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

	def chat_recvMessage(self, **kwargs):
		super(OneRoomUser, self).chat_recvMessage(**kwargs)
		creator = kwargs.get('Creator',  kwargs.get('creator', None))
		cid = kwargs.get('ContainerId',  kwargs.get('containerId', None))
		if cid == self.room and creator != self.username:
			self.heart_beats = 0
		else:
			self.recv_messages.pop(kwargs['ID'] , None)

	def wait_4_room(self, max_beats=5):
		self.heart_beats = 0
		while self.heart_beats < max_beats and not self.room:
			self.nextEvent()

		if self.heart_beats >= max_beats and not self.room:
			raise CouldNotEnterRoom()

	# ======================

	def post_messages(self, room_id, entries, delay=0.25, min_phrases=5):
		self.post_random_messages(room_id, entries, min_phrases, delay=delay)

	# ======================

	@property
	def room(self):
		if not self._room and len(self.rooms) > 0:
			self._room = self.first_room
		return self._room

# ----------------------------

class Host(OneRoomUser):

	def __init__(self, username, occupants, *args, **kwargs):
		super(Host, self).__init__(username=username, **kwargs)
		self.occupants = occupants
		self.online = set()

	@property
	def users_online(self):
		return list(sorted(self.online))

	def chat_presenceOfUserChangedTo(self, username, status):
		if status == 'Online' and username in self.occupants:
			self.online.add(username)
			self.heart_beats = 0

	def __call__(self, *arg, **kwargs):

		delay = kwargs.get('delay', 0.25)
		entries = kwargs.get('entries', None)
		inReplyTo = kwargs.get("inReplyTo", None)
		references = kwargs.get("references", None)
		containerId = kwargs.get('containerId', None)
		connect_event = kwargs.get('connect_event', None)
		max_heart_beats = kwargs.get('max_heart_beats', 3)
		
		try:
			self.ws_connect()

			# wait users are connected

			self.heart_beats = 0
			while self.heart_beats < max_heart_beats and len(self.online) < len(self.occupants):
				self.nextEvent()
			
			self.enterRoom(	occupants=self.occupants, containerId=containerId,
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
			sio = StringIO()
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback, file=sio)
			sio.seek(0)

			self.exception = e
			self.traceback = sio.read()
		finally:
			self.ws_capture_and_close()

# ----------------------------

class Invitee(OneRoomUser):

	def __call__(self, *args, **kwargs):
		try:
			delay = kwargs.get('delay', 0.25)
			entries = kwargs.get('entries', None)
			max_heart_beats = kwargs.get('max_heart_beats', 2)

			# connect
			self.ws_connect()

			# check for an connect event
			event = kwargs.get('connect_event', None)
			event.wait(60)

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
			sio = StringIO()
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback, file=sio)
			sio.seek(0)

			self.exception = e
			self.traceback = sio.read()
			# print self.traceback 
		finally:
			self.ws_capture_and_close()

User = Invitee

# ----------------------------

def run_chat(containerId, host_user, invitees, entries=None, delay=0.25, 
			 max_heart_beats=3, use_threads=True, host_class=Host, invitee_class=Invitee, 
			 server=SOCKET_IO_HOST, port=SOCKET_IO_PORT, **kwargs):

	runnables = []
	entries = entries or random.randint(5, 20)
	connect_event = threading.Event() if use_threads else multiprocessing.Event()

	host = host_class(host_user, invitees, host=server, port=port)
	users = [invitee_class(username=name, host=server, port=port) for name in invitees]

	required_args = {'entries':entries, 'containerId':containerId, 'connect_event':connect_event,
					 'delay':delay, 'max_heart_beats':max_heart_beats}

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

if __name__ == '__main__':
	cid = 'tag:nextthought.com,2011-10:AOPS-HTML-prealgebra.0'
	host = 'test.user.1@nextthought.com'
	users =['test.user.%s@nextthought.com' % s for s in range(2, 11)]
	all_users = [host] + users
	
	entries = 50
	server = 'localhost'
	
	def create_fl(username):
		import uuid
		from nti.integrationtests.dataserver.client import DataserverClient
		from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD
		
		endpoint = 'http://%s:%s/dataserver2' % (server, 8081)
		ds = DataserverClient(endpoint=endpoint, credentials=(username, DEFAULT_USER_PASSWORD))
		list_name = 'cfl-%s-%s' % (username, str(uuid.uuid4()).split('-')[0])
		
		users = list(all_users)
		users.remove(username)
		ds.createFriendsListWithNameAndFriends(list_name, users)
		
	for username in all_users:
		create_fl(username)
		
	result = run_chat(cid, host, users, entries=entries, delay=2, use_threads=True, server=server, max_heart_beats=3)
	for r in result:
		print r.username, len(list(r.sent)), len(list(r.received)), r.exception


