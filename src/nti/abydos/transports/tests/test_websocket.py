#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property

import unittest

from .. import websocket

class TestWebSocket(unittest.TestCase):
	
	@unittest.skip("localhost")
	def test_connect(self):
		ws = websocket.create_server_connection('localhost',
												8081,
												'test.user.1@nextthought.com',
												'temp001', is_secure=False)

		assert_that(ws, has_property('connected', is_(True)))
		assert_that(ws.recv(), is_not(none()))
		ws.close()
		assert_that(ws, has_property('connected', is_(False)))
