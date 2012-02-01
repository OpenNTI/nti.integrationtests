'''
Created on Oct 18, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Results
from nti.integrationtests.legacy.generalpurpose.deletetestcase import DeleteTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_results

class V3_ResultsServer401UnauthorizedUserGetTestCase(DeleteTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Results()
		super(V3_ResultsServer401UnauthorizedUserGetTestCase, self).__init__(ServerTestV3_results, self.constants_object, *args, **kwargs)

	def test_Server401UnauthorizedUserGetTestCase(self):
		self.unauthorizedDeleteTest(username=self.constants_object.otherUser, overRide=True)
	
if __name__ == '__main__':
	import unittest
	unittest.main()
