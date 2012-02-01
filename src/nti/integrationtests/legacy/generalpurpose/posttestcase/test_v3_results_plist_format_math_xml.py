'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Results
from nti.integrationtests.legacy.generalpurpose.posttestcase import PostTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_results
from nti.integrationtests.legacy.generalpurpose.utilities.body_data_extracter import URL_Skipped_Question_Assessment
from nti.integrationtests.legacy.generalpurpose.utilities.url_formatter import PlistFormat

class V3_ResultsServer201PlistFormatMathXMLPostTestCase(PostTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Results()
		super(V3_ResultsServer201PlistFormatMathXMLPostTestCase, self).__init__(ServerTestV3_results, self.constants_object, *args, **kwargs)

	def test_Server201PlistFormatMathXMLPostTestCase(self):
		self.successfulAddPostTest(urlGroup=self.constants_object.URL_USER_MATH_XML, data=self.constants_object.OPEN_MATH_XML_INFO, body=self.constants_object.MATH_XML_RETURN, bodyDataExtracter=URL_Skipped_Question_Assessment(), fmt=PlistFormat())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
