'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V2Constants
from nti.integrationtests.legacy.generalpurpose.posttestcase import PostTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV2

class V2Server201StandardPostTestCase(PostTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server201StandardPostTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server201StandardPostTestCase(self):
		self.successfulAddPostTest()
	
if __name__ == '__main__':
	import unittest
	unittest.main()
