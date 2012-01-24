import random
import unittest

from user_chat_objects import HostUserChatTest

class TestChatTranscript(HostUserChatTest):
		
	def setUp(self):
		super(TestChatTranscript, self).setUp()
		
		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]
		
	def test_transcript(self):
		
		entries = random.randint(20, 50)
		one, two = self._run_chat(self.container, entries, self.user_one, self.user_two)
		for u in (one, two):
			self.assert_(u.exception == None, "User %s caught exception %s" % (u.username, u.exception))
			
		self.assert_(one.room, "User '%s' could not enter room" % one.username)
		self.assert_(two.room, "User '%s' could not enter room" % two.username)
		room_id = two.room
		
		all_msgs = []
		map(lambda x: all_msgs.append(x), one.sent)
		map(lambda x: all_msgs.append(x), one.received)
		
		self.ds.set_credentials(user=one.username, password=one.password)
		t = self.ds.get_transcript(self.container, room_id)
		
		self.assertTrue(t.has_key(u'RoomInfo'), 'Could not find room info')
		
		ri = t[u'RoomInfo']
		self.assertEqual(entries*2, ri.messageCount, 'Unexpected message count')
		self.assertEqual(room_id, ri.id, 'Unexpected room id')
		
		self.assertTrue(t.has_key(u'Messages'), 'Incomplete message')
		messages = t['Messages']
		for m in messages:
			body = m['Body'][0]
			self.assert_(body != None, 'Invalid body')
			self.assert_(m[u'ID'], 'No id for message found')
			self.assertEqual(m[u'ContainerId'], room_id, 'Unexpected message room id')
			self.assertEqual(m[u'Status'], u'st_POSTED', 'Unexpected message status')
			self.assert_(body in all_msgs, 'Unexpected message')

if __name__ == '__main__':
	unittest.main()
	