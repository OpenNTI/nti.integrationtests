'''
Created on Oct 10, 2011

@author: ltesti
'''

from servertests.generalpurpose import V2Constants
from servertests.generalpurpose.puttestcase import PutTests
from servertests.generalpurpose.utilities.catagory import ServerTestV2

class V2Server200StandardPutTestCase(PutTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V2Constants()
		super(V2Server200StandardPutTestCase, self).__init__(ServerTestV2, self.constants_object, *args, **kwargs)

	def test_Server200StandardPutTestCase(self):
		self.okPutTest()
	
if __name__ == '__main__':
	import unittest
	unittest.main()