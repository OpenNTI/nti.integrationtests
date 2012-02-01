'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.puttestcase import PutTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2
from nti.integrationtests.legacy.generalpurpose.utilities.body_data_extracter import URL_DefaultV2

class V2PutStandardTest(PutTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2PutStandardTest, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server401JsonFormatIncorrectPasswordPutTestCase(self):
		self.unauthorizedPutTestJsonFormat(password=self.constants_object.incorrectPassword, bodyDataExtracter=URL_DefaultV2())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
