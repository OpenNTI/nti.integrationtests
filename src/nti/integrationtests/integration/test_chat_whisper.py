import time
import random
import unittest

import test_chat_multi_user
import user_chat_objects
from websocket_interface import WHISPER_CHANNEL

from hamcrest import has_key
from hamcrest import has_item
from hamcrest import assert_that

class TestWhisperChat(test_chat_multi_user.TestMultiUserChat):
	
	chatting_users = 5

	def test_chat(self):
		entries = random.randint(2, 5)
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		mapping  = {}
		for u in users[1:]:
			mapping[u.username] = [m.text for m in u.received_on_channel(WHISPER_CHANNEL)]
			
		host = users[0]
		whispered = list(host.sent_on_channel(WHISPER_CHANNEL))
		
		for m in whispered:
			r = m.recipients[0]
			assert_that(mapping, has_key(r), "Whispered message was not recieved by %s" % r)
			assert_that(mapping[r], has_item(m.text))
			
	def _create_host(self, username, occupants):
		return Host(username, occupants, port=self.port)
		
# ----------------------------

class Host(user_chat_objects.Host):
		
	def post_messages(self, room_id, *args, **kwargs):
		entries = random.randint(20, 30)
		for _ in range(entries):
			msg = self.generate_message(5, 10)
			if random.random() <= 0.4:
				whisper_to = random.choice(self.users_online)
				self.chat_postMessage(message=msg, containerId=room_id,\
									  channel=WHISPER_CHANNEL, recipients=[whisper_to])
			else:
				self.chat_postMessage(message=msg, containerId=room_id)
			time.sleep(0.25)
			
if __name__ == '__main__':
	unittest.main()
