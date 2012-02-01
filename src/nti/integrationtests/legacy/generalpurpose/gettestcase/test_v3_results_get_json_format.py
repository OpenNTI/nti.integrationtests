'''
Created on Oct 4, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Results
from nti.integrationtests.legacy.generalpurpose.gettestcase import GetTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_results
from nti.integrationtests.legacy.generalpurpose.utilities.url_formatter import JsonFormat

class V3ResultsServer200JsonFormatGetTestCase(GetTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Results()
		super(V3ResultsServer200JsonFormatGetTestCase, self).__init__(ServerTestV3_results, self.constants_object, *args, **kwargs)

	def test_Server200JsonFormatGetTestCase(self):
		self.okGetTest(fmt=JsonFormat())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
