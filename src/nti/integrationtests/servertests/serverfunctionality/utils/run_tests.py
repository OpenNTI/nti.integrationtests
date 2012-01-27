'''
Created on Jan 25, 2012

@author: ltesti
'''
'''
Created on Jan 13, 2012

@author: ltesti
'''

import os
import json
import glob

from nti.integrationtests.servertests.serverfunctionality.utils import USERNAME, PASSWORD, URL, DATASERVER, PATH_TO_TESTS
from nti.integrationtests.servertests.serverfunctionality.utils.generaterequest import ServerRequest
from nti.integrationtests.servertests.serverfunctionality.utils.serverdata import Workspace
from nti.integrationtests.servertests import DataServerTestCase

from nti.integrationtests.servertests.serverfunctionality.utils.url_formatter import NoFormat
from nti.integrationtests.servertests.serverfunctionality.utils.url_formatter import JsonFormat
from nti.integrationtests.servertests.serverfunctionality.utils.url_formatter import PlistFormat

from nti.integrationtests.servertests.serverfunctionality.testrunner.post_runner import PostObject
from nti.integrationtests.servertests.serverfunctionality.testrunner.get_runner import GetObject
from nti.integrationtests.servertests.serverfunctionality.testrunner.get_collection_runner import GetGroupObject
from nti.integrationtests.servertests.serverfunctionality.testrunner.put_runner import PutObject
from nti.integrationtests.servertests.serverfunctionality.testrunner.delete_runner import DeleteObject

from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import NoteBodyTester
from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import HighlightBodyTester
from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import FriendsListBodyTester
from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import CanvasBodyTester
from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import CanvasShapeBodyTester
from nti.integrationtests.servertests.serverfunctionality.utils.response_assert import CanvasPolygonShapeBodyTester


def setup():
	DataServerTestCase.setUpClass()
	
def teardown():
	DataServerTestCase.tearDownClass()
	
def open_data_file(file_path):
	try:
		with open(file_path,"r") as f:
			content = json.loads(f.read())
		return content
	except: 
		return False

def get_body_inspector(testType):
	if testType == 'application/vnd.nextthought.note': return NoteBodyTester()
	if testType == 'application/vnd.nextthought.highlight': return HighlightBodyTester()
	if testType == 'application/vnd.nextthought.friendslist': return FriendsListBodyTester()
	if testType == 'application/vnd.nextthought.canvas': return CanvasBodyTester()
	if testType == 'application/vnd.nextthought.canvasshape': return CanvasShapeBodyTester()
	if testType == 'application/vnd.nextthought.canvascircleshape': return CanvasShapeBodyTester()
	if testType == 'application/vnd.nextthought.canvaspolygonshape': return CanvasPolygonShapeBodyTester()
	else: return False

def get_request_type(testType):
	if testType == "Post": return PostObject()
	if testType == "Get": return GetObject()
	if testType == "GetGroup": return GetGroupObject()
	if testType == "Put": return PutObject()
	if testType == "Delete": return DeleteObject()
	else: return False
	
def get_format(formatt):
	if formatt == "NoFormat": return NoFormat()
	if formatt == "JsonFormat": return JsonFormat()
	if formatt == 'PlistFormat': return PlistFormat()
	else: return False
	
def get_info(test_path):
	tests = []
	for test in test_path:
		test_file = test.split(PATH_TO_TESTS)[1]
		test = test_file.split('.json')[0]
		tests.append(test)
	return tests
	
def run_tests():
	noFormat = NoFormat()
	requests = ServerRequest()
	
	#aquires the server doc
	dataserverURL = URL + DATASERVER
	serverDocRequest = requests.get(url=dataserverURL, username=USERNAME, password=PASSWORD)
	parsedBody = noFormat.read(serverDocRequest)
	workspace = Workspace.new_from_dict(parsedBody['Items'][0])
	
	# the tests that will be ran
	test_paths = glob.glob(PATH_TO_TESTS + '*')
#	tests = get_info(test_path)
	
	# massive nested for loops that generate all the tests to be ran
	for collection in workspace.collections:
		href = workspace.collections[collection].href
		for accept in workspace.collections[collection].accepts:
			for test_path in test_paths:
				# variables meant to prevent 
				# bad tests from stopping 
				# other tests from running
				badTest = False
				error = None
				testValues = open_data_file(test_path)
				if accept == testValues['data_type']:
					bodyInspector = get_body_inspector(testValues['data_type'])
					# if the test file doesnt exist, catch that error and continue
					try:
						for testType in testValues["test_types"]:
							testTypeObj = get_request_type(testType)
							for responseType in testValues['response_types']:
								for formatt in testValues['input_formats']:
									formatt = get_format(formatt)
									kwargs = {'href':href, 'objRunner':testValues, 'bodyTester':bodyInspector, 'format':formatt, \
										'responseTypes':testValues['response_types'][responseType], 'testTypeObj': testTypeObj}
									# looks for false values in kwargs. False values come from something being expected
									# to exist as a testing parameter however does not actually exist. 
									# This catches it and reports it
									for testParameter in kwargs:
										if kwargs[testParameter] is False and badTest is False: 
											badTest = True
											error = testParameter
									if badTest is True: 
										badTest = False
										yield terminate, error, get_info(test_paths)
									elif testType == 'Post' and testValues['response_types'][responseType]['classification'] == 'NotFound': pass
									elif testType != 'Post' and testType != 'Put' and \
										testValues['response_types'][responseType]['classification'] == 'BadData': pass
									else: yield testTypeObj.makeRequest, kwargs
					# if a TypeError is caught for a nonexistant file, 
					# report the failure to run those tests
					except TypeError: 
						error = 'objRunner'
						yield terminate, error, get_info(test_paths)
			if badTest is True:
				badTest = False
				yield terminate, error, get_info(test_paths)

# reports the error in starting the test
def terminate(error, test):
	if error == 'objRunner': message = 'no file avalible to open named %s' % test
	elif error == 'bodyTester': message = 'wrong test name was received to run %s tests' % test
	elif error == 'testTypeObj': message = 'unsupported request type was received to run %s tests' % test
	elif error == 'format': message = 'unsupported format was received to run %s tests' % test
	else: message = None
	assert False, message
		