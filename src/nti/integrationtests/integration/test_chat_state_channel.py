import unittest

from nti.integrationtests.integration import test_chat_whisper
from nti.integrationtests.chat.socketio_interface import STATE_CHANNEL

from hamcrest import ( has_entry, is_not, assert_that, has_length )

max_channel_messsages = 10
max_state_channel_messsages = 10
pcnt_state_channel_messages = 1.0

class TestChatWithState(test_chat_whisper.TestWhisperChat):
	
	chatting_users = 4
	channel = STATE_CHANNEL

	def _create_host(self, username, occupants, **kwargs):
		return StateChannelHost(username, occupants, port=self.port, **kwargs)
		
	def _check_channel_messages(self, mapping, messages):
		assert_that(messages, has_length(max_state_channel_messsages))
		for m in messages:
			content = m.content
			assert_that(content, is_not(None))
			assert_that(content, has_entry('state','active'))
			
class StateChannelHost(test_chat_whisper.ChannelHost):
	
	channel = STATE_CHANNEL
	pcnt = pcnt_state_channel_messages
	min_entries = max_channel_messsages
	max_entries = max_channel_messsages

	def generate_channel_msg(self, counter):
		return {'state':'active'}
	
	def generate_channel_msg_recipients(self):
		return []
	
	def can_send_on_default_channel(self, send_on_channel):
		return True
			
if __name__ == '__main__':
	unittest.main()
