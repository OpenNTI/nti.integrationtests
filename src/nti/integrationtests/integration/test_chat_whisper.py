import time
import random
import unittest

from nti.integrationtests.chat import objects
from nti.integrationtests.integration import test_chat_multi_user
from nti.integrationtests.chat.socketio_interface import WHISPER_CHANNEL

from hamcrest import ( has_key, has_item, assert_that )

class TestWhisperChat(test_chat_multi_user.TestMultiUserChat):
	
	chatting_users = 5
	channel = WHISPER_CHANNEL
	
	# override test
	def test_multiuser_chat(self):
		entries = random.randint(2, 5)
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		mapping  = {}
		for u in users[1:]:
			mapping[u.username] = [m.text for m in u.received_on_channel(self.channel)]
			
		host = users[0]
		sentOnChannel = list(host.sent_on_channel(self.channel))
		self._check_channel_messages(mapping, sentOnChannel)
			
	def _create_host(self, username, occupants, **kwargs):
		return ChannelHost(username, occupants, port=self.port, **kwargs)
		
	def _check_channel_messages(self, mapping, messages):
		for m in messages:
			r = m.recipients[0]
			assert_that(mapping, has_key(r), "%s message was not recieved by %s" % (self.channel,r))
			assert_that(mapping[r], has_item(m.text))
			
class ChannelHost(objects.Host):
	
	pcnt = 0.4
	min_entries = 20
	max_entries = 30
	tick_entries = 5
	channel = WHISPER_CHANNEL
	
	def generate_channel_msg(self, counter):
		return self.generate_message(k=5)
	
	def generate_channel_msg_recipients(self):
		return [random.choice(self.users_online)]
	
	def can_send_on_default_channel(self, send_on_channel):
		return send_on_channel
	
	def post_messages(self, room_id, entries, delay=0.25, *args, **kwargs):
		entries = random.randint(self.min_entries, self.max_entries)
		for c in range(entries):
			counter = c + 1
			sentOnChannel = random.random() <= self.pcnt
			if sentOnChannel:
				msg = self.generate_channel_msg(counter)
				channel_to = self.generate_channel_msg_recipients()
				self.chat_postMessage(message=msg, containerId=room_id,
									  channel=self.channel, recipients=channel_to)
			
			if self.can_send_on_default_channel(sentOnChannel):
				msg = self.generate_message(k=5)
				self.chat_postMessage(message=msg, containerId=room_id)
				
			time.sleep(delay)
			if counter % self.tick_entries == 0:
				self.send_heartbeat()
			
if __name__ == '__main__':
	unittest.main()
