from hamcrest import assert_that, has_length, has_key, greater_than_or_equal_to

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
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		ghost = users[0]
		chatters = users[1:]
		shadowed_user = chatters[0]
		ghost_msgs = ghost.recv_messages
		shadowed_msgs = shadowed_user.recv_messages

		assert_that( ghost_msgs, has_length( greater_than_or_equal_to( 2 * len(shadowed_msgs ) ) ) )

		for k in shadowed_msgs.keys():
			assert_that( ghost_msgs, has_key( k ) )


	def _create_host(self, username, occupants):
		return Ghost(self.users_to_shadow, username=username, occupants=occupants, port=self.port)



class Ghost(user_chat_objects.Host):

	def __init__(self, users_to_shadow, *args, **kwargs):
		super(Ghost, self).__init__(*args, **kwargs)
		self.users_to_shadow = users_to_shadow

	def wait_4_room(self, max_beats=5):
		super(Ghost, self).wait_4_room(max_beats=max_beats)
		self.shadowUsers(self.room, self.users_to_shadow)

	def post_messages(self, room_id, *args, **kwargs):
		pass

if __name__ == '__main__':
	unittest.main()
