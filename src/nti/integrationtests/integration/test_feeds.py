#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import gzip
import time
import unittest
from io import BytesIO

from lxml import etree

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

from nose.plugins.attrib import attr
from hamcrest import (assert_that, not_none, has_length, greater_than_or_equal_to, contains_string)

@attr(level=3, type="feeds")
class TestFeeds(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestFeeds, self).setUp()
		self.container = 'test.feeds.%s' % time.time()
		self.ds.set_credentials(self.owner)

	def _find_item_in_rss(self, dso, feed):
		root = etree.XML(feed)
		find = etree.XPath("//item[guid=$nid]")
		items = find(root, nid=dso['id'])
		assert_that(items, has_length(1))
		item = items[0]
		return item

	def _find_item_in_atom(self, dso, feed):
		root = etree.XML(feed)
		find = etree.XPath("//t:entry[t:id=$nid]", namespaces={'t':'http://www.w3.org/2005/Atom'})
		entries = find(root, nid=dso['id'])
		assert_that(entries, has_length(1))
		entry = entries[0]
		return entry

	def test_simple_feed(self):
		# create note
		created_obj = self.ds.create_note('my note', self.container, sharedWith=[self.target[0]])

		# test rss feed
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		item = self._find_item_in_rss(created_obj, feed)
		assert_that(item, not_none())

		# test atom feed
		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		entry = self._find_item_in_atom(created_obj, feed)
		assert_that(entry, not_none())

		self.ds.delete_object(created_obj)

	def test_feed_note_with_canvas(self):

		# create note w/ canvas
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		created_obj = self.ds.create_note(['my note with canvas', canvas], self.container, sharedWith=[self.target[0]])

		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		item = self._find_item_in_rss(created_obj, feed)
		assert_that(item.find('description').text, contains_string('my note with canvas'))

		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		entry = self._find_item_in_atom(created_obj, feed)
		assert_that(entry.find('t:summary', namespaces={'t':'http://www.w3.org/2005/Atom'}).text, contains_string('my note with canvas'))

		self.ds.delete_object(created_obj)

	def test_feed_note_non_ascii_body(self):

		# create note
		unicode_string = u"hello Â"
		created_obj = self.ds.create_note(unicode_string, self.container, sharedWith=[self.target[0]])

		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		item = self._find_item_in_rss(created_obj, feed)
		assert_that(item.find('description').text, contains_string(unicode_string))

		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		entry = self._find_item_in_atom(created_obj, feed)
		assert_that(entry.find('t:summary', namespaces={'t':'http://www.w3.org/2005/Atom'}).text, contains_string(unicode_string))

		self.ds.delete_object(created_obj)

	def test_multiple_notes_gzip(self):
		size = 10
		for i in xrange(0, size):
			self.ds.create_note('Note number %s' % i, self.container, sharedWith=[self.target[0]])

		feed = self.ds.get_rss_feed(self.container, credentials=self.target, gzip=True)
		feed = feed if isinstance(feed, gzip.GzipFile) else BytesIO(feed)
		root = etree.parse(feed)
		count_elements = etree.XPath("count(//item)")
		assert_that(count_elements(root), greater_than_or_equal_to(size))

		feed = self.ds.get_atom_feed(self.container, credentials=self.target, gzip=True)
		feed = feed if isinstance(feed, gzip.GzipFile) else BytesIO(feed)
		root = etree.parse(feed)
		count_elements = etree.XPath("count(//t:entry)", namespaces={'t':'http://www.w3.org/2005/Atom'})
		assert_that(count_elements(root), greater_than_or_equal_to(size))

	def test_not_in_feed_after_del(self):
		note = self.ds.create_note('my note', self.container, sharedWith=[self.target[0]])
		note['body'] = ['my modified note']
		self.ds.update_object(note)

		# check feed after uodate
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		root = etree.XML(feed)
		find = etree.XPath("//item[guid=$nid]")
		items = find(root, nid=note['id'])
		assert_that(items, has_length(1))

		# delete and check feed
		self.ds.delete_object(note)
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		if feed:
			root = etree.XML(feed)
			find = etree.XPath("//item[guid=$nid]")
			items = find(root, nid=note['id'])
			assert_that(items, has_length(0))

if __name__ == '__main__':
	unittest.main()
