'''
Created on Oct 4, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.gettestcase import GetTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2

class V2Server200StandardGetTestCase(GetTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server200StandardGetTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server200StandardGetTestCase(self):
		self.okGetTest()
	
if __name__ == '__main__':
	import unittest
	unittest.main()
