import time
import uuid
import random
import threading
import collections

from websocket_interface import Graph
from websocket_interface import Serverkill
from websocket_interface import InActiveRoom
from websocket_interface import CouldNotEnterRoom
from websocket_interface import NotEnoughOccupants

from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD
from nti.integrationtests import DataServerTestCase
from nti.integrationtests.dataserver.server import PORT
from nti.integrationtests.dataserver.server import SERVER_HOST

SOCKET_IO_HOST	= SERVER_HOST
SOCKET_IO_PORT	= PORT

phrases = (	"Yellow brown", 
			"Blue red green render purple?",
			"Alpha beta", 
			"Gamma delta epsilon omega.",
			"One two",
			"Three rendered four five.",
			"Quick went",
			"Every red town.",
			"Yellow uptown", 
			"Interest rendering outer photo!",
			"Preserving extreme", 
			"Chicken hacker"
			"Shoot To Kill",
			"Bloom, Split and Deviate",
			"Rankle the Seas and the Skies",
			"Lightning Flash Flame Shell",
			"Flower Wind Rage and Flower God Roar, Heavenly Wind Rage and Heavenly Demon Sneer",
			"All Waves, Rise now and Become my Shield, Lightning, Strike now and Become my Blade", 
			"Cry, Raise Your Head, Rain Without end.",
			"Sting All Enemies To Death",
			"Reduce All Creation to Ash",
			"Sit Upon the Frozen Heavens", 
			"Call forth the Twilight")

# ----------------------------

class BasicChatTest(DataServerTestCase):
		
	def setUp(self):
		super(BasicChatTest, self).setUp()
		self.container = 'test.user.container.%s' % time.time()
		
	# ======================
	
	@classmethod
	def static_initialization(cls):
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		cls.create_users(ds_client=ds_client)
	
	@classmethod
	def create_users(cls, max_users=10, create_friends_lists=True, ds_client=None):
		for x in range(1, max_users):
			name = 'test.user.%s@nextthought.com' % x
			cls.user_names.append(name)
			
		if create_friends_lists:
			for u in cls.user_names:
				friends = list(cls.user_names)
				friends.remove(u)
				cls.register_friends(username=u, friends=friends, ds_client=ds_client)
		
	@classmethod
	def generate_user_name(self):
		return '%s@nextthought.com' % str(uuid.uuid4()).split('-')[0]
		
	@classmethod
	def register_friends(cls, username, friends, password=DEFAULT_USER_PASSWORD, ds_client=None):
		
		if isinstance(friends, basestring) or not isinstance(friends, collections.Iterable):
			friends = [friends]
		elif not isinstance(friends, list):
			friends = list(set(friends))
		
		list_name = 'cfl-%s-%s' % (username, str(uuid.uuid4()).split('-')[0])
		
		ds = cls.new_client((username, password)) if not ds_client else ds_client
		credentials = ds.get_credentials()
		try:
			ds.set_credentials(user=username, password=password)
			ds.createFriendsListWithNameAndFriends(list_name, friends)
		finally:
			ds.set_credentials(credentials)
		
		return list_name
	
# ----------------------------

class BasicUser(Graph):
	def __init__(self, *args, **kwargs):
		if not kwargs.has_key('host'):
			kwargs['host'] = SOCKET_IO_HOST
		
		if not kwargs.has_key('port'):
			kwargs['port'] = SOCKET_IO_PORT
			
		Graph.__init__(self, *args, **kwargs)
		self.exception = None
					
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
		return " ".join(random.sample(phrases, random.randint(aMin, aMax)))
	
	def post_random_messages(self, room_id, entries=None, a_min=3, a_max=10, delay=None):
		entries = entries or random.randint(a_min, a_max)
		for _ in xrange(entries):
			content = self.generate_message()
			self.chat_postMessage(message=unicode(content), containerId=room_id)
			if delay:
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
		
		entries = kwargs.get('entries', None)
		containerId = kwargs.get('containerId', None)
		connect_event = kwargs.get('connect_event', None)
		inReplyTo = kwargs.get("inReplyTo", None)
		references = kwargs.get("references", None)
		
		try:
			if not self.ws_connected:
				self.ws_connect()
			
			# wait users are connected
			
			self.heart_beats = 0
			while self.heart_beats < 3 and len(self.online) < len(self.occupants):
				self.nextEvent()				
				
			self.enterRoom(	occupants=self.occupants, containerId=containerId,
							inReplyTo=inReplyTo, references=references)
			self.wait_4_room()	
			connect_event.set()	
			
			room_id = self.room
			if room_id:
				self.post_messages(room_id, entries)
			else:
				raise Exception('%s did not enter a chat room' % self.username)
			
			# process messages
			self.wait_heart_beats(3)
					
		except Exception, e:
			self.exception = e
		finally:
			self.ws_capture_and_close()
				
# ----------------------------
	
class User(OneRoomUser):
		
	def __call__(self, *args, **kwargs):
		try:
			entries = kwargs.get('entries', None)
					
			# connect
			if not self.ws_connected:
				self.ws_connect()
	
			# check for an connect event
			event = kwargs.get('connect_event', None)
			event.wait(60)
					
			self.wait_4_room()
				
			# write any messages
			room_id = self.room
			if room_id:
				self.post_messages(room_id, entries)
			else:
				raise Exception('%s did not enter a chat room' % self.username)
					
			# get any message
			self.wait_heart_beats(2)
					
		except Exception, e:
			self.exception = e
		finally:
			self.ws_capture_and_close()
			
# ---------------------------

class HostUserChatTest(BasicChatTest):
			
	def _create_host(self, username, occupants):
		return Host(username, occupants, port=self.port)
	
	def _create_user(self, username):
		return User(username=username, port=self.port)
	
	def _run_chat(self, containerId, entries, *denizens, **kwargs):
		
		runnables = []
		connect_event = threading.Event()
		
		occupants = denizens[1:]
		host = self._create_host(denizens[0], occupants)
		users = [self._create_user(name) for name in occupants]	
		
		required_args = {'entries':entries, 'containerId':containerId, 'connect_event':connect_event}
		
		h_args = dict(kwargs)
		h_args.update(required_args)
		h_t = threading.Thread(target=host, kwargs=h_args)
		h_t.start()
		runnables.append(h_t)
		
		# wait for host to connect
		time.sleep(1)
		
		for u in users:
			u_args = dict(kwargs)
			u_args.update(required_args)
			u_t=threading.Thread(target=u, kwargs=u_args)
			u_t.start()
			runnables.append(u_t)
	
		for t in runnables:
			t.join()
			
		result = [host]
		result.extend(users)
		
		return result

	