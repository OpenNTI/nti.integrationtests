import os
import unittest
	
from nti.contenttests.html_parser import Meta
from nti.contenttests.html_parser import parse_html_file

from hamcrest import is_
from hamcrest import has_key
from hamcrest import assert_that

def pprint(obj, stream=None, indent=1):
	import pprint
	pprint.pprint(obj, stream=stream, indent=indent)
	
class TestHtmlParser(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls.cp1 = os.path.join(os.path.dirname(__file__), 'cp_1.html')
		cls.add = os.path.join(os.path.dirname(__file__), 'add.html')

	def setUp(self):
		super(TestHtmlParser, self).setUp()
		
	def test_parser(self):
		d = parse_html_file(self.add)
		assert_that(d, has_key('meta'))
		assert_that(d['meta'], has_key('NTIID'))
		assert_that(d['meta']['NTIID'], is_(Meta('NTIID', 'tag:nextthought.com,2011-10:AOPS-HTML-prealgebra.addition')))
		
if __name__ == '__main__':
	unittest.main()