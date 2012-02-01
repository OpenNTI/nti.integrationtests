'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.puttestcase import PutTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2
from nti.integrationtests.legacy.generalpurpose.utilities.url_formatter import PlistFormat

class V2Server200PlistFormatNonExistTypePutTestCase(PutTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server200PlistFormatNonExistTypePutTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server200PlistFormatNonExistTypePutTestCase(self):
		self.okPutTest(url=self.constants_object.URL_USER_NONEXIST_TYPE, urlGroup=self.constants_object.URL_USER_NONEXIST_TYPE_NO_ID, fmt=PlistFormat())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
