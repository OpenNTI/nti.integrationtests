# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from .. import alias, make_repr
from .constants import DEFAULT_CHANNEL

class Room(object):

	id = alias('ID')
	active = alias('Active')
	occupants = alias('Occupants')
	moderated = alias('Moderated')
	containerId = alias('ContainerId')

	def __init__(self, ID=None, Occupants=None, Active=True, Moderated=False,
				 ContainerId=None, **kwargs):

		assert ID, "must specify a valid room ID"
		assert Occupants != None, "must specify valid room occupants"

		self.ID = ID
		self.Active = Active
		self.Occupants = Occupants
		self.Moderated = Moderated
		self.ContainerId = ContainerId

	def __str__(self):
		return self.ID

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or self.ID == other.ID
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.ID)
		return xhash

_Room = Room  # BWC

class Message(object):

	id = alias('ID')
	content = alias('message')

	def __init__(self, ID=None, message=None, channel=DEFAULT_CHANNEL, inReplyTo=None,
				 recipients=None, creator=None, lastModified=None, containerId=None,
				 **kwargs):
		self.ID = ID
		self.creator = creator
		self.message = message
		self.inReplyTo = inReplyTo
		self.recipients = recipients
		self.containerId = containerId
		self.channel = channel or DEFAULT_CHANNEL

	@property
	def text(self):
		result = None
		if isinstance(self.message, (list, tuple)):
			result = unicode(self.message[0]) if self.message else None
		elif self.message:
			result = unicode(self.message)
		return result

	def __str__(self):
		return str(self.message)

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or self.ID == other.ID
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.ID)
		return xhash

_Message = Message  # BWC

class RecvMessage(_Message):

	def __init__(self, **kwargs):
		super(_RecvMessage, self).__init__(**kwargs)
		self.lastModified = kwargs.get('lastModified', 0)

_RecvMessage = RecvMessage  # BWC

class PostMessage(_Message):
	pass

_PostMessage = PostMessage  # BWC
