#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import unittest
from datetime import datetime

from webob import datetime_utils

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

from nti.integrationtests.integration import container_of_length

from hamcrest import (is_, is_not, assert_that, has_length)

from nose.plugins.attrib import attr

@attr(level=3)
class TestBasicNotes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)
	string = u'a note to post'
	title = u'a note title'

	def setUp(self):
		super(TestBasicNotes, self).setUp()
		self.ds.set_credentials(self.owner)
		self.container = 'test.user.container.%s' % time.time()

	def test_create_note_with_string(self):
		created_obj = self.ds.create_note(self.string, self.container, title=self.title)
		assert_that(created_obj['body'][0], is_(self.string))
		assert_that(created_obj['id'], is_not(None))
		assert_that(created_obj['title'], is_(self.title))
	
	def test_create_note_with_string_in_array(self):
		created_obj = self.ds.create_note([self.string], self.container)
		assert_that(created_obj['body'][0], is_(self.string))
		
	def test_create_note_with_string_and_object_in_array(self):
		created_canvas = self.create_canvas()
		created_obj = self.ds.create_note([self.string, created_canvas], self.container)
		assert_that(created_obj['body'][0], is_(self.string))
		assert_that(created_obj['body'][1], is_(Canvas))
		
	def test_create_note_with_object_in_array(self):
		created_canvas = self.create_canvas()
		created_obj =  self.ds.create_note([created_canvas], self.container)
		assert_that(created_obj['body'][0], is_(Canvas))

	def create_canvas(self):
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		return self.ds.create_object(canvas)
	
	def test_create_empty_note(self):
		try:
			self.ds.create_note(u'', self.container)
			self.fail('an empty not was created')
		except:
			pass
		
	def test_create_empty_container(self):
		try:
			self.ds.create_note(self.string, u'')
			self.fail('a note in an empty container was created')
		except:
			pass
		
	def test_inreply_to(self):
		note_1 = self.ds.create_note(self.string, self.container)
		
		nid = note_1['id']
		note_2 =  self.ds.create_note('reply to n1', self.container, inReplyTo=nid)
		
		assert_that(note_2['body'][0]), is_("reply to n1")
		assert_that(note_2['inReplyTo'], is_(nid))
		
	def test_references(self):
		nids =[]
		for x in range(1,5):
			references = nids if x == 4 else None
			created_note = self.ds.create_note(['note %s' % x], self.container, references=references)
			nids.append(created_note['id'])
		assert_that(created_note['references'], has_length(len(nids)-1))
		
	def test_sharedWith(self):		
		created_note = self.ds.create_note(self.string, self.container, sharedWith=[self.target[0]])
		assert_that(created_note['sharedWith'], is_([self.target[0]]))
		
	def test_note_title_indexing(self):
		note = self.ds.create_note(u'The Asauchi breaks away to reveal Hollow Ichigo', self.container, title='At the palace of Oetsu')
		result = self.ds.search_user_content("Asauchi")
		assert_that(result, container_of_length(1))

		result = self.ds.search_user_content("Oetsu")
		assert_that(result, container_of_length(1))

		self.ds.delete_object(note)
		result = self.ds.search_user_content("Asauchi")
		assert_that(result, container_of_length(0))

		result = self.ds.search_user_content("Oetsu")
		assert_that(result, container_of_length(0))

	def test_conditional_put(self):
		note = self.ds.create_note(u'The man who stole the bankai', self.container, title='At the seretei')
		note['body'] = ['Kill the captains with their stolen bankai']
		headers = {'If-Unmodified-Since': 'Wed, 09 Oct 1973 15:07:09 GMT'}
		try:
			self.ds.update_object(note, headers=headers)
			self.fail('conditional put failed')
		except:
			pass

	def test_conditional_delete(self):
		note = self.ds.create_note(u'Things that live together should die together', self.container, title='Stern ritter')
		since = datetime.fromtimestamp(time.time() - 10000)
		sdate = datetime_utils.serialize_date(since)
		headers = {'If-Unmodified-Since': sdate}
		try:
			self.ds.delete_object(note, headers=headers)
			self.fail('conditional delete failed')
		except:
			pass

if __name__ == '__main__':
	unittest.main()
