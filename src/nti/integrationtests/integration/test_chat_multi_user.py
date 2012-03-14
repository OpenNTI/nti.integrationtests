import random
import unittest

from user_chat_objects import HostUserChatTest

class TestMultiUserChat(HostUserChatTest):
	
	chatting_users = 4
	
	def setUp(self):
		super(TestMultiUserChat, self).setUp()
		self.chat_users = self.user_names[:self.chatting_users]
	
	def test_chat(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, *self.chat_users)
		
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare(users[i], users[i+1])
			self._compare(users[i+1], users[i])
		
	def _compare(self, sender, receiver):
		
		_sent = list(sender.sent)
		self.assertTrue(len(_sent) > 0, "%s did not send any messages" % sender)
		
		_recv = list(receiver.received)
		self.assertTrue(len(_recv) > 0, "%s did not get any messages" % receiver)
		
		for s in _sent:
			self.assert_(s in _recv, "%s did not get message '%s' from %s" % (receiver, s, sender))
	
if __name__ == '__main__':
	unittest.main()
