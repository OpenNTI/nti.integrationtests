'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Quizzes
from nti.integrationtests.legacy.generalpurpose.puttestcase import PutTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_quizzes
from nti.integrationtests.legacy.generalpurpose.utilities.url_formatter import PlistFormat

class V3_QuizzesServer200PlistFormatPutTestCase(PutTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Quizzes()
		super(V3_QuizzesServer200PlistFormatPutTestCase, self).__init__(ServerTestV3_quizzes, self.constants_object, *args, **kwargs)

	def test_Server200PlistFormatPutTestCase(self):
		self.okPutTest(fmt=PlistFormat())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
