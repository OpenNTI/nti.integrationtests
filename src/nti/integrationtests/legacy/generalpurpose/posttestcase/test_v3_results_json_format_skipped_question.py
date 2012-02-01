'''
Created on Oct 10, 2011

@author: ltesti
'''

from nti.integrationtests.legacy.generalpurpose import V3Constants_Results
from nti.integrationtests.legacy.generalpurpose.posttestcase import PostTests
from nti.integrationtests.legacy.generalpurpose.utilities.catagory import ServerTestV3_results
from nti.integrationtests.legacy.generalpurpose.utilities.body_data_extracter import URL_Skipped_Question_Assessment
from nti.integrationtests.legacy.generalpurpose.utilities.url_formatter import JsonFormat

class V3_ResultsServer201JsonFormatSkippedQuestionPostTestCase(PostTests):

	def __init__(self, *args, **kwargs):
		self.constants_object = V3Constants_Results()
		super(V3_ResultsServer201JsonFormatSkippedQuestionPostTestCase, self).__init__(ServerTestV3_results, self.constants_object, *args, **kwargs)

	def test_Server201JsonFormatSkippedQuestionPostTestCase(self):
		self.successfulAddPostTest(data=self.constants_object.SKIPPED_QUESTION_INFO, body=self.constants_object.SKIPPED_QUESTION_RETURN, bodyDataExtracter=URL_Skipped_Question_Assessment(), fmt=JsonFormat())
	
if __name__ == '__main__':
	import unittest
	unittest.main()
