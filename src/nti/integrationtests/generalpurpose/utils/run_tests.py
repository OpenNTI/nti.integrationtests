import os
import sys
import glob
import json

from nose.tools import with_setup

from nti.integrationtests.contenttypes.servicedoc import Workspace

from nti.integrationtests.generalpurpose import PATH_TO_TESTS
from nti.integrationtests.generalpurpose.utils.response_assert import MIME_TYPE_REGISTRY
from nti.integrationtests.generalpurpose.utils.generaterequest import ServerRequest

# ----------------------------

test_global_data = {}
formatter_module = None
request_type_module = None

def import_module(module_name):
	__import__(module_name, globals(), locals(), [], -1)
	return sys.modules[module_name]

request_type_module = import_module("nti.integrationtests.generalpurpose.utils")
formatter_module = import_module("nti.integrationtests.generalpurpose.utils.url_formatter")
	
# ----------------------------

def setup_func():
	pass

def teardown_func():
	pass

# ----------------------------

def open_data_file(file_path):
	with open(file_path,"r") as f:
		content = json.loads(f.read())
	return content
	
def get_request_type(test_type):
	local_name = '%sObject' % test_type
	clazz = request_type_module.__dict__[local_name]
	return clazz()

def get_format(format_type):
	clazz = formatter_module.__dict__[format_type]
	return clazz()
	
def get_json_files(test_path=PATH_TO_TESTS):
	return glob.glob(test_path + '/*.json')		
	
def get_body_inspector(test_type):
	clazz = MIME_TYPE_REGISTRY[test_type]
	return clazz()
		
def get_workspaces(url, username, password):
	formatter = get_format('NoFormat')
	document = ServerRequest().get(url=url, username=username, password=password)
	parsedBody = formatter.read(document)
	workspace = Workspace.new_from_dict(parsedBody['Items'][0])
	return workspace
	
@with_setup(setup_func, teardown_func)
def test_generator():
	
	host = os.environ.get('host', 'localhost')
	port = int(os.environ.get('port', '8081'))
	endpoint = "http://%s:%s/dataserver2" % (host, port)
	
	username =  os.environ.get('username', 'test.user.1@nextthought.com')
	password =  os.environ.get('password', 'temp001')
	
	workspace = get_workspaces(endpoint, username, password)
	
	# the tests that will be ran
	test_files_path = os.path.expanduser(os.environ.get('test_files', PATH_TO_TESTS))
	test_paths = get_json_files(test_files_path)

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
				
				test_values = open_data_file(test_path)

				if accept == test_values['data_type'] or test_values['data_type'] == 'application/vnd.nextthought.quiz':
					body_inspector = get_body_inspector(test_values['data_type'])
					
					# if the test file doesnt exist, catch that error and continue
					try:
						for test_type in test_values["test_types"]:
							test_type_obj = get_request_type(test_type)
							for responseType in test_values['response_types']:
								for input_formatt in test_values['input_formats']:
									input_formatt = get_format(input_formatt)
									kwargs = {	'href' : href,
												'objRunner' : test_values, 
												'bodyTester': body_inspector, 
												'format': input_formatt, 
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
										yield terminate, error, test_path
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
						terminate, error, test_path
				
def terminate(error, test):
	test = os.path.basename(test)
	if error == 'objRunner': 
		message = 'no file avalible to open named %s' % test
	elif error == 'bodyTester': 
		message = 'wrong test name was received to run %s tests' % test
	elif error == 'test_type_obj':
		message = 'unsupported request type was received to run %s tests' % test
	elif error == 'format': 
		message = 'unsupported format was received to run %s tests' % test
	else: 
		message = None
	assert False, message
		
if __name__ == '__main__':	
	for v in test_generator():
		print v
