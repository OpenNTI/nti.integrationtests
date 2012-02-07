import sys
import glob
import json
from nose.tools import eq_

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.generalpurpose import USERNAME, PASSWORD, URL, DATASERVER, PATH_TO_TESTS
from nti.integrationtests.generalpurpose.utils.generaterequest import ServerRequest
from nti.integrationtests.generalpurpose.utils.serverdata import Workspace

from nti.integrationtests.generalpurpose.utils.url_formatter import NoFormat
from nti.integrationtests.generalpurpose.utils.url_formatter import JsonFormat
from nti.integrationtests.generalpurpose.utils.url_formatter import PlistFormat

from nti.integrationtests.generalpurpose.utils.response_assert import NoteBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import HighlightBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import FriendsListBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import CanvasBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import CanvasShapeBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import CanvasPolygonShapeBodyTester
from nti.integrationtests.generalpurpose.utils.response_assert import QuizTester

class TestClass(object):

	def open_data_file(self, file_path):
		try:
			with open(file_path,"r") as f:
				content = json.loads(f.read())
				return content
		except: 
			return False

	def get_body_inspector(self, test_type):
		if test_type == 'application/vnd.nextthought.note': 
			return NoteBodyTester()
		elif test_type == 'application/vnd.nextthought.highlight': 
			return HighlightBodyTester()
		elif test_type == 'application/vnd.nextthought.friendslist': 
			return FriendsListBodyTester()
		elif test_type == 'application/vnd.nextthought.canvas': 
			return CanvasBodyTester()
		elif test_type == 'application/vnd.nextthought.canvasshape':
			return CanvasShapeBodyTester()
		elif test_type == 'application/vnd.nextthought.canvascircleshape':
			return CanvasShapeBodyTester()
		elif test_type == 'application/vnd.nextthought.canvaspolygonshape':
			return CanvasPolygonShapeBodyTester()
		elif test_type == 'application/vnd.nextthought.quiz': 
			return QuizTester()
		else: 
			return False

	def get_request_type(self, test_type):
		module_name = "nti.integrationtests.generalpurpose.utils"
		try:
			__import__(module_name, globals(), locals(), [], -1)
			mod = sys.modules[module_name]
		except ImportError:
			return False
	
		local_name = '%sObject' % test_type
		clazz = mod.__dict__[local_name] if local_name in mod.__dict__ else None
		return clazz() if clazz else False
	
	def get_format(self, formatt):
		if formatt == "NoFormat": return NoFormat()
		if formatt == "JsonFormat": return JsonFormat()
		if formatt == 'PlistFormat': return PlistFormat()
		else: return False
	
	def get_info(self, test_path):
		tests = []
		for test in test_path:
			test_file = test.split(PATH_TO_TESTS)[1]
			test = test_file.split('.json')[0]
			tests.append(test)
		return tests
	
	def setup(self):
		self.called = ['setup']
		
	def teardown(self):
		print "teardown called in", self
		eq_(self.called, ['setup'])
		self.called.append('teardown')
	
	def test(self):
		noFormat = NoFormat()
		requests = ServerRequest()
	
		#aquires the server doc
		dataserverURL = URL + DATASERVER
		serverDocRequest = requests.get(url=dataserverURL, username=USERNAME, password=PASSWORD)
		parsedBody = noFormat.read(serverDocRequest)
		workspace = Workspace.new_from_dict(parsedBody['Items'][0])
	
		# the tests that will be ran
		test_paths = glob.glob(PATH_TO_TESTS + '*')
	
		# massive nested for loops that generate all the tests to be ran
		for collection in workspace.collections:
			href = workspace.collections[collection].href
			for accept in workspace.collections[collection].accepts:
				for test_path in test_paths:
					# variables meant to prevent 
					# bad tests from stopping 
					# other tests from running
					error = None
					bad_test = False
				
					test_values = self.open_data_file(test_path)
					if accept == test_values['data_type'] or test_values['data_type'] == 'application/vnd.nextthought.quiz':
						body_inspector = self.get_body_inspector(test_values['data_type'])
						# if the test file doesnt exist, catch that error and continue
						try:
							for test_type in test_values["test_types"]:
								test_type_obj = self.get_request_type(test_type)
								for responseType in test_values['response_types']:
									for formatt in test_values['input_formats']:
										formatt = self.get_format(formatt)
										kwargs = {	'href' : href,
												'objRunner' : test_values, 
												'bodyTester': body_inspector, 
												'format': formatt, 
												'responseTypes': test_values['response_types'][responseType],
												'test_type_obj': test_type_obj }
									
										# looks for false values in kwargs. False values come from something being expected
										# to exist as a testing parameter however does not actually exist. 
										# This catches it and reports it
										for test_parameter in kwargs:
											if not kwargs[test_parameter] and not bad_test: 
												bad_test = True
												error = test_parameter
											
										if bad_test: 
											bad_test = False
											yield self.terminate, error, self.get_info(test_paths)
										elif test_type == 'Post' and test_values['response_types'][responseType]['classification'] == 'NotFound':
											pass
										elif test_type != 'Post' and test_type != 'Put' and \
											test_values['response_types'][responseType]['classification'] == 'BadData':
											pass
										else:
											yield test_type_obj.makeRequest, kwargs
										
						# if a TypeError is caught for a nonexistant file, 
						# report the failure to run those tests
						except TypeError: 
							error = 'objRunner'
							yield self.terminate, error, self.get_info(test_paths)
						
					if bad_test:
						bad_test = False
						yield self.terminate, error, self.get_info(test_paths)

	# reports the error in starting the test
	def terminate(self, error, test):
		if error == 'objRunner': message = 'no file avalible to open named %s' % test
		elif error == 'bodyTester': message = 'wrong test name was received to run %s tests' % test
		elif error == 'test_type_obj': message = 'unsupported request type was received to run %s tests' % test
		elif error == 'format': message = 'unsupported format was received to run %s tests' % test
		else: message = None
		assert False, message
		
	def check(self, i):
		print "check called in", self
		expect = ['setup']
		eq_(self.called, expect)


if __name__ == '__main__':	
	TestClass().get_request_type('Post')
