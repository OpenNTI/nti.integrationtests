import unittest

from nti.integrationtests.chat import objects
from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from hamcrest import ( assert_that, has_length, greater_than_or_equal_to )

class TestShadowedChat(HostUserChatTest):

	def setUp(self):
		super(TestShadowedChat, self).setUp()
		self.chat_users = self.user_names[:3]
		self.users_to_shadow = [self.chat_users[1]]

	def test_chat(self):
		entries = 17
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		ghost = users[0]
		chatters = users[1:]
		shadowed_user = chatters[0]
		ghost_msgs = ghost.recv_messages
		shadowed_msgs = shadowed_user.sent_messages

		assert_that( ghost_msgs, has_length( greater_than_or_equal_to( 2 * len(shadowed_msgs ) ) ) )

		# TODO: This is not a very good test. We want to check that the 
		# received messages match the shadowed messages, but we don't have
		# correct ID information at this point

	def _create_host(self, username, occupants):
		return Ghost(self.users_to_shadow, username=username, occupants=occupants, port=self.port)


class Ghost(objects.Host):

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
