import random
import unittest

from nti.integrationtests.dataserver.client import DataserverClient

from user_chat_objects import HostUserChatTest

class TestSimpleChat(HostUserChatTest):
	
	@classmethod
	def static_initialization(cls):
		
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		cls.create_users(create_friends_lists=False, ds_client=ds_client)
		
		cls.user_one = cls.user_names[0]
		cls.user_two = cls.user_names[1]
		cls.user_three = cls.user_names[2]
		
		cls.register_friends(cls.user_one, [cls.user_two], ds_client=ds_client)
		cls.register_friends(cls.user_two, [cls.user_one], ds_client=ds_client)
		cls.register_friends(cls.user_three, [cls.user_one, cls.user_two], ds_client=ds_client)
		
		cls.user_four = cls.user_names[3]
		cls.register_friends(cls.user_four, [cls.user_one, cls.user_two], ds_client=ds_client)
		
		cls.user_five = cls.generate_user_name()
	
	def test_chat(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, self.user_one, self.user_two)
		
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare(users[i], users[i+1])
			self._compare(users[i+1], users[i])
		
	def test_chat_user_not_friend(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, self.user_three, self.user_four)
		
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare(users[i], users[i+1])
			self._compare(users[i+1], users[i])
		
	def test_chat_unregistered_user(self):
		entries = random.randint(5, 10)
		one, two = self._run_chat(self.container, entries, self.user_one, self.user_five)
		self.assert_(len(one.users_online) == 0, "No user was supposed to be online")
		self.assert_(two.exception, "Invalid Auth was expected for %s" % two.username)
		
	def _compare(self, sender, receiver):
		_sent = list(sender.sent)
		self.assertTrue(len(_sent) > 0, "%s did not send any messages" % sender)
		
		_recv = list(receiver.received)
		self.assertTrue(len(_recv) > 0, "%s did not get any messages" % receiver)
		
		self.assertEqual(_sent, _recv, "%s did not get all messages from %s" % (receiver, sender))
	
if __name__ == '__main__':
	unittest.main()
	