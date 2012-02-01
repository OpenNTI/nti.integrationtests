'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.posttestcase import PostTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2

class V2Server500PlistFormatWrongUserPostTestCase(PostTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server500PlistFormatWrongUserPostTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server500PlistFormatWrongUserPostTestCase(self):
		self.improperInfoPostTestPlistFormat(info=self.constants_object.WRONG_INFO)
	
if __name__ == '__main__':
	import unittest
	unittest.main()
