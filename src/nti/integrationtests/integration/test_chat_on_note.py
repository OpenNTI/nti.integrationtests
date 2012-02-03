import time
import unittest

from nti.integrationtests.contenttypes import Note
from nti.integrationtests.contenttypes import TranscriptSummary

import user_chat_objects
from user_chat_objects import HostUserChatTest

class TestChatOnNote(HostUserChatTest):
	
	def setUp(self):
		super(TestChatOnNote, self).setUp()
		
		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]
		self.user_three = self.user_names[2]
		
		self.host_messages = ("Yellow brown", "Blue red green render purple?", "Every red town.")
		self.user_messages = ("Three rendered four five.", "Preserving extreme", "Chicken hacker")

		self.ds.set_credentials((self.user_one, self.default_user_password))
	
	def test_chat(self):

		# creates a note
		created_note = self.ds.create_note('A note to share', self.container, adapt=True)
		
		# shares the note
		shared_note = self.ds.share_object(created_note, [self.user_two], adapt=True)
			
		# creates a chat in a room determined by the note that was just created
		note_id = shared_note['id']
		params = {'references' : [note_id], 'inReplyTo': note_id }
		one, two = self._run_chat(self.container, 0, self.user_one, self.user_two, **params)
		for u in (one, two):
			self.assert_(u.exception == None, "User %s caught exception %s" % (u.username, u.exception))
			
		room_id = one.room
			
		# aquires the use generated data
		self.ds.set_credentials(user=two.username, password=two.password)
		ugd = self.ds.get_user_generated_data(self.container)
		
		# determines that both the note and the chat are found in the users generated data
		items = ugd['Items']
		self.assertEqual(len(items), 2, "Expected a item count")
		
		transcript = None
		found_note = False
		for item in items:
			found_note = found_note or isinstance(item, Note)
			if isinstance(item, TranscriptSummary):
				transcript = item
				
		self.assert_(transcript, "Transcript not found in UGD")		
		self.assert_(found_note, "Note not found in UGD")	
		
		self.assertEqual(transcript.container, room_id)
		self.assertEqual(transcript.roomInfo.inReplyTo, created_note['id'])
		self.assertEqual(transcript.roomInfo.messageCount, 6)
		
		# share the note w/ someone else
		self.ds.set_credentials(user=one.username, password=one.password)
		shared_note = self.ds.share_object(created_note, [self.user_three], adapt=True)
		
		# we aren't instant	Wait some arbitrary time.
		self.ds.wait_for_event()
		
		# gets user three's user generated data
		ugd = self.ds.get_user_generated_data(self.container, credentials=(self.user_three, self.default_user_password))
		items = ugd['Items']
		
		self.assertEqual(1, len(items), "Expected a item count")
		self.assert_(isinstance(item, Note), "Expected item")
		
		self.ds.delete_object(created_note)
		
	def _create_host(self, username, occupants):
		return Host(self.host_messages, username=username, occupants=occupants, port=self.port)
	
	def _create_user(self, username):
		return User(self.user_messages, username=username, port=self.port)
	
# ---------------------------

class Host(user_chat_objects.Host):
		
	def __init__(self, host_messages, *args, **kwargs):
		super(Host, self).__init__(*args, **kwargs)
		self.host_messages = host_messages
		
	def post_messages(self, room_id, *args, **kwargs):
		for m in self.host_messages:
			self.chat_postMessage(message=unicode(m), containerId=room_id)
			time.sleep(0.25)
		
class User(user_chat_objects.User):
		
	def __init__(self, user_messages, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.user_messages = user_messages
		
	def post_messages(self, room_id, *args, **kwargs):
		for m in self.user_messages:
			self.chat_postMessage(message=unicode(m), containerId=room_id)
			time.sleep(0.25)
				
if __name__ == '__main__':
	unittest.main()
