import os
import unittest
	
from nti.contenttests.html_parser import parse_html_file

class TestHtmlParser(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls.cp1 = os.path.join(os.path.dirname(__file__), 'cp_1.html')

	def setUp(self):
		super(TestHtmlParser, self).setUp()
		
	def test_parser(self):
		parse_html_file(self.cp1)
		
if __name__ == '__main__':
	unittest.main()