import random
import unittest

import user_chat_objects
from user_chat_objects import HostUserChatTest

class TestShadowedChat(HostUserChatTest):
	
	def setUp(self):
		super(TestShadowedChat, self).setUp()	
		self.chat_users = self.user_names[:3]
		self.users_to_shadow = [self.chat_users[1]]
		
	def test_chat(self):
		entries = random.randint(10, 20)
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception %s" % (u.username, u.exception))
		
		ghost = users[0]
		chatters = users[1:]
		shadowed_user = chatters[0]
		ghost_msgs = ghost.recv_messages
		shadowed_msgs = shadowed_user.recv_messages
	
		self.assertEqual(2*len(shadowed_msgs), len(ghost_msgs), \
						"Ghost %s did not get all messages from shadowed %s" % (ghost, shadowed_user))
		
		for k, _ in shadowed_msgs.items():
			self.assert_(ghost_msgs.has_key(k), "Ghost %s did not get message with id %s" % (ghost, k))

	def _create_host(self, username, occupants):
		return Ghost(self.users_to_shadow, username=username, occupants=occupants, port=self.port)
	
# ----------------------------
			
class Ghost(user_chat_objects.Host):
		
	def __init__(self, users_to_shadow, *args, **kwargs):
		super(Ghost, self).__init__(*args, **kwargs)
		self.users_to_shadow = users_to_shadow
	
	def wait_4_room(self):
		super(Ghost, self).wait_4_room()
		self.shadowUsers(self.room, self.users_to_shadow)	
	
	def post_messages(self, room_id, *args, **kwargs):
		pass
		
if __name__ == '__main__':
	unittest.main()
	