# -*- coding: utf-8 -*-

import time
import unittest

from lxml import etree

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

from hamcrest import (assert_that, not_none, has_length, is_)

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
		items = find(root, nid = dso['id'])
		assert_that(items, has_length(1))
		item = items[0]
		return item
	
	def _find_item_in_atom(self, dso, feed):
		root = etree.XML(feed)
		find = etree.XPath("//t:entry[t:id=$nid]", namespaces={'t':'http://www.w3.org/2005/Atom'})
		entries = find(root, nid = dso['id'])
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
		created_obj =  self.ds.create_note(['my note with canvas', canvas], self.container, sharedWith=[self.target[0]])
		
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		item = self._find_item_in_rss(created_obj, feed)
		assert_that(item.find('description').text, is_('my note with canvas'))
		
		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		entry = self._find_item_in_atom(created_obj, feed)
		assert_that(entry.find('t:summary', namespaces={'t':'http://www.w3.org/2005/Atom'}).text, is_('my note with canvas'))
		
		self.ds.delete_object(created_obj)
		
	def test_feed_note_non_ascii_body(self):
		
		# create note
		unicode_string = u"hello Â"
		created_obj =  self.ds.create_note(unicode_string, self.container, sharedWith=[self.target[0]])
		
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		item = self._find_item_in_rss(created_obj, feed)
		assert_that(item.find('description').text, is_(unicode_string))
		
		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		entry = self._find_item_in_atom(created_obj, feed)
		assert_that(entry.find('t:summary', namespaces={'t':'http://www.w3.org/2005/Atom'}).text, is_(unicode_string))
	
		self.ds.delete_object(created_obj)
		
if __name__ == '__main__':
	unittest.main()
