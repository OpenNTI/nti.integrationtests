'''
Created on Oct 4, 2011

@author: ltesti
'''

from servertests.generalpurpose import V2Constants
from servertests.generalpurpose.gettestcase import GetTests
from servertests.generalpurpose.utilities.catagory import ServerTestV2

class V2Server200NoUserGetTestCase(GetTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server200NoUserGetTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server200NoUserGetTestCase(self):
		self.unauthorizedGetTest(username=self.constants_object.noUser)
	
if __name__ == '__main__':
	import unittest
	unittest.main()