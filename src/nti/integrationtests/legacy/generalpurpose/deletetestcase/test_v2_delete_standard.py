'''
Created on Oct 18, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.deletetestcase import DeleteTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2

class V2Server204StandardGetTestCase(DeleteTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server204StandardGetTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server204StandardGetTestCase(self):
		self.successfulDeleteTest()
	
if __name__ == '__main__':
	import unittest
	unittest.main()
