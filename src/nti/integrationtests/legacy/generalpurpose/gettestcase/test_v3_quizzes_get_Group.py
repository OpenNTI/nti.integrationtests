'''
Created on Oct 4, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Quizzes
from nti.integrationtests.legacy.generalpurpose.gettestcase import GetTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_quizzes
from nti.integrationtests.legacy.generalpurpose.utilities.body_data_extracter import URL_QuizGroup

class V3QuizzesServer200GetGroupGetTestCase(GetTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Quizzes()
		super(V3QuizzesServer200GetGroupGetTestCase, self).__init__(ServerTestV3_quizzes, self.constants_object, *args, **kwargs)

	def test_Server200GetGroupGetTestCase(self):
		self.okGetTest(self.constants_object.URL_POST, bodyDataExtracter=URL_QuizGroup())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
