import time
import unittest

from lxml import etree
from pyquery import PyQuery

from nti.integrationtests import DataServerTestCase

from hamcrest import (assert_that, not_none, has_length)

class TestFeeds(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestFeeds, self).setUp()
		self.container = 'test.feeds.%s' % time.time()
		self.ds.set_credentials(self.owner)

	def test_simple_feed(self):

		created_obj = self.ds.create_note('my note', self.container, sharedWith=[self.target[0]])
		feed = self.ds.get_rss_feed(self.container, credentials=self.target)
		d = PyQuery(feed)
		item = d('guid').filter(lambda i, this: PyQuery(this).text() == created_obj['id'])
		assert_that(item, not_none())
		
		feed = self.ds.get_atom_feed(self.container, credentials=self.target)
		root = etree.XML(feed)
		find = etree.XPath("//t:entry[t:id=$nid]", namespaces={'t':'http://www.w3.org/2005/Atom'})
		entry = find(root, nid = created_obj['id'])
		assert_that(entry, has_length(1))
		
		self.ds.delete_object(created_obj)
		

if __name__ == '__main__':
	unittest.main()
