# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

import six
import time
import uuid
import threading
import collections

from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import User

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import DEFAULT_USER_PASSWORD

class BasicChatTest(DataServerTestCase):

	def setUp(self):
		super(BasicChatTest, self).setUp()
		self.container = 'test.user.container.%s' % time.time()

	@classmethod
	def static_initialization(cls):
		cls.create_users()

	@classmethod
	def create_users(cls, max_users=10, create_friends_lists=False, ds_client=None):
		for x in range(1, max_users):
			name = 'test.user.%s@nextthought.com' % x
			cls.user_names.append(name)

		if create_friends_lists:
			result = []
			for u in cls.user_names:
				friends = list(cls.user_names)
				friends.remove(u)
				result.append(cls.register_friends(username=u, friends=friends, ds_client=ds_client))
		else:
			result = ()
		return result

	@classmethod
	def generate_user_name(self):
		return '%s@nextthought.com' % str(uuid.uuid4()).split('-')[0]

	@classmethod
	def register_friends(cls, username, friends, password=DEFAULT_USER_PASSWORD, ds_client=None):

		if isinstance(friends, six.string_types) or not isinstance(friends, collections.Iterable):
			friends = [friends]
		elif not isinstance(friends, list):
			friends = list(set(friends))

		list_name = str(uuid.uuid4())
		ds = cls.new_client((username, password)) if not ds_client else ds_client
		credentials = ds.get_credentials()
		try:
			ds.set_credentials(user=username, password=password)
			result = ds.createFriendsListWithNameAndFriends(list_name, friends)
			return result
		finally:
			ds.set_credentials(credentials)

class HostUserChatTest(BasicChatTest):

	host_transport = 'websocket'
	user_transport = 'websocket'
	
	def _create_host(self, username, occupants, **kwargs):
		return Host(username, occupants, port=self.port, **kwargs)

	def _create_user(self, username, **kwargs):
		return User(username=username, port=self.port, **kwargs)

	def _run_chat(self, containerId, entries, *members, **kwargs):

		runnables = []
		connect_event = threading.Event()

		occupants = members[1:]
		host = self._create_host(members[0], occupants, transport=self.host_transport)
		users = [self._create_user(name, transport=self.user_transport) for name in occupants]

		required_args = {'entries':entries, 'containerId':containerId, 'connect_event':connect_event}

		h_args = dict(kwargs)
		h_args.update(required_args)
		h_t = threading.Thread(target=host, kwargs=h_args)
		h_t.start()
		runnables.append(h_t)

		# wait for host to connect
		time.sleep(1)

		for u in users:
			u_args = dict(kwargs)
			u_args.update(required_args)
			u_t = threading.Thread(target=u, kwargs=u_args)
			u_t.start()
			runnables.append(u_t)

		for t in runnables:
			t.join()

		result = [host]
		result.extend(users)

		return result
