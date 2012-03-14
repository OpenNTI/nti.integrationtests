import unittest
	
import user_chat_objects
from user_chat_objects import HostUserChatTest

class TestChatUserleavesEarly(HostUserChatTest):
	
	def setUp(self):
		super(TestChatUserleavesEarly, self).setUp()
		self.chat_users = self.user_names[:3]
		self.leave_early_user = self.chat_users[2]
		
	def test_chat(self):
		entries = 2
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))
			
		total_sent =  0
		for u in users:
			total_sent = total_sent + len(list(u.sent))
			
		self.assertEqual(total_sent, 10, "Incorrect number of messages sent")
		self.assertEqual( len(list(users[2].received)), 6, "Unexpected number of messages") 
		
	def _create_user(self, username):
		early = username == self.leave_early_user
		return User(leaves_early=early, username=username, port=self.port)
	
	def _create_host(self, username, occupants):
		return Host(username=username, occupants=occupants, port=self.port)
			
# ----------------------------

class Host(user_chat_objects.Host):
	def post_messages(self, room_id, entries, *args, **kwargs):
		self.post_random_messages(room_id, entries)
		self.wait_heart_beats(2)
		self.post_random_messages(room_id, entries)

	def __call__(self, *args, **kwargs):
		super(Host, self).__call__(*args, **kwargs)
		#print 'done host'
		
class User(user_chat_objects.User):
		
	def __init__(self, leaves_early=False, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.leaves_early = leaves_early
		
	def process_messages(self):
		return not self.leaves_early
				
	def post_messages(self, room_id, entries, *args, **kwargs):
		self.post_random_messages(room_id, entries)
		self.wait_heart_beats(1)
		if not self.leaves_early:
			self.wait_heart_beats(2)
			self.post_random_messages(room_id, entries)

	def __call__(self, *args, **kwargs):
		super(User, self).__call__(*args, **kwargs)
		#print 'done', self.username
		
if __name__ == '__main__':
	unittest.main()
