'''
Created on Oct 4, 2011

@author: ltesti
'''

from servertests.generalpurpose import V3Constants_Quizzes
from servertests.generalpurpose.gettestcase import GetTests
from servertests.generalpurpose.utilities.catagory import ServerTestV3_quizzes

class V3QuizzesServer200StandardGetTestCase(GetTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Quizzes()
		super(V3QuizzesServer200StandardGetTestCase, self).__init__(ServerTestV3_quizzes, self.constants_object, *args, **kwargs)

	def test_Server200StandardGetTestCase(self):
		self.okGetTest()
	
if __name__ == '__main__':
	import unittest
	unittest.main()