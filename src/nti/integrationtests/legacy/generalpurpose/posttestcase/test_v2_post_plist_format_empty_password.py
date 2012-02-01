'''
Created on Oct 10, 2011

@author: ltesti
'''

from servertests.generalpurpose import V2Constants
from servertests.generalpurpose.posttestcase import PostTests
from servertests.generalpurpose.utilities.catagory import ServerTestV2

class V2Server401PlistFormatEmptyPasswordPostTestCase(PostTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server401PlistFormatEmptyPasswordPostTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server401PlistFormatEmptyPasswordPostTestCase(self):
		self.unauthorizedPostTestPlistFormat(password=self.constants_object.emptyPassword)
	
if __name__ == '__main__':
	import unittest
	unittest.main()