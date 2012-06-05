import os
import glob
import json
import time
import tempfile

import sys
import nose
import argparse

from nose.util import resolve_name

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.contenttypes.servicedoc import Workspace

from nti.integrationtests.generalpurpose import PATH_TO_TESTS
from nti.integrationtests.generalpurpose.utils.response_assert import MIME_TYPE_REGISTRY
from nti.integrationtests.generalpurpose.utils.generaterequest import ServerRequest

from nti.integrationtests.generalpurpose.testrunner.get_runner import GetObject
from nti.integrationtests.generalpurpose.testrunner.put_runner import PutObject
from nti.integrationtests.generalpurpose.testrunner.post_runner import PostObject
from nti.integrationtests.generalpurpose.testrunner.delete_runner import DeleteObject
from nti.integrationtests.generalpurpose.testrunner.get_collection_runner import GetGroupObject


host = None
port = None
endpoint = None
username = None
password = None
root_dir = None
dataserver = None
use_coverage = None


def get_env_vars():
	global host, port, endpoint, username, password, root_dir, use_coverage

	host = os.environ.get('host', 'localhost')
	port = int(os.environ.get('port', get_open_port()))
	endpoint = "http://%s:%s/dataserver2" % (host, port)
	username = os.environ.get('username', 'test.user.1@nextthought.com')
	password = os.environ.get('password', 'temp001')
	root_dir = os.environ.get('root_dir', tempfile.mktemp(prefix="ds.data.gpt.", dir="/tmp"))
	use_coverage = os.environ.get('use_coverage', 'False').lower() == 'true'

def setup():
	global dataserver

	get_env_vars()

	dataserver = DataserverProcess(port=port, root_dir=root_dir)
	if use_coverage:
		dataserver.start_server_with_coverage()
	else:
		dataserver.start_server()

def teardown():
	if use_coverage:
		dataserver.terminate_server_with_coverage()
	else:
		dataserver.terminate_server()


def open_data_file(file_path):
	with open(file_path,"r") as f:
		content = json.loads(f.read())
	return content

def get_request_type(test_type):
	clazz = sys.modules[__name__].__dict__[test_type + 'Object']
	return clazz()

def get_format(format_type):
	clazz = resolve_name("nti.integrationtests.generalpurpose.utils.url_formatter.%s" % format_type)
	return clazz()

def get_json_files(test_path=PATH_TO_TESTS):
	return glob.glob(test_path + '/*.json')

def get_body_inspector(test_type):
	clazz = MIME_TYPE_REGISTRY[test_type]
	return clazz()

def get_workspaces(url, username, password):
	formatter = get_format('NoFormat')
	document = ServerRequest().get(url=url, username=username, password=password)
	parsed_body = formatter.read(document)
	workspace = Workspace.new_from_dict(parsed_body['Items'][0])
	return workspace

def test_generator():
	if not dataserver.is_running():
		print "Waiting for server to come-up"
		time.sleep(5)

	workspace = get_workspaces(endpoint, username, password)

	# the tests that will be ran
	test_files_path = os.path.expanduser(os.environ.get('test_files', PATH_TO_TESTS))
	test_paths = get_json_files(test_files_path)

	# massive nested for loops that generate all the tests to be ran
	for test_path in test_paths:

		for collection in workspace.collections:
			href = workspace.collections[collection].href
			for accept in workspace.collections[collection].accepts:
				# variables meant to prevent
				# bad tests from stopping
				# other tests from running
				error = None
				bad_test = False

				test_values = open_data_file(test_path)

				if accept == test_values['data_type']:
					body_inspector = get_body_inspector(test_values['data_type'])

					# if the test file doesnt exist, catch that error and continue
					try:
						for test_type in test_values["test_types"]:
							for input_formatt in test_values['input_formats']:
								input_formatt = get_format(input_formatt)
							test_type_obj = get_request_type(test_type)
							for responseType in test_values['response_types']:
								for input_formatt in test_values['input_formats']:
									input_formatt = get_format(input_formatt)
									kwargs = {	'endpoint'		: endpoint,
												'username'		: username,
												'password'		: password,
												'href' 			: href,
												'objRunner'		: test_values,
												'bodyTester'	: body_inspector,
												'format'		: input_formatt,
												'responseTypes'	: test_values['response_types'][responseType],
												'test_type_obj'	: test_type_obj }

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
									elif accept == 'application/vnd.nextthought.quizresult':
										yield test_type_obj.makeQuizResultRequest, kwargs
									else:
										yield test_type_obj.makeRequest, kwargs

					# if a TypeError is caught for a nonexistant file,
					# report the failure to run those tests
					except TypeError:
						error = 'objRunner'
						yield terminate, error, test_path

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


def main(args = None):
	args = args or sys.argv[1:]

	parser = argparse.ArgumentParser(prog='General Purpose Tests')
	parser.add_argument('-uc', '--use_coverage', help='use coverage', action='store_true', default = False)
	parser.add_argument('-cr', '--coverage_report', help='create coverage report', action='store_true', default = False)
	parser.add_argument('-rd', '--root_dir', help='root directory', required=False)
	parser.add_argument('-p', '--port', help='server port', type=int, required=False, default=None)
	opts = parser.parse_args(args)

	root_dir = opts.root_dir if opts.root_dir else tempfile.mktemp(prefix="ds.data.gpt.", dir="/tmp")

	os.environ['root_dir'] = os.path.expanduser(root_dir)
	os.environ['use_coverage'] = 'True' if opts.use_coverage else 'False'
	os.environ['port'] = str(opts.port if opts.port else get_open_port())

	print "Running options...."
	print "\tServer port = %s" % os.environ['port']
	print "\tUsing coverage = %s" % opts.use_coverage
	print "\tRoot dir = %s\n" % root_dir

	# simply ignore the nose parameters # XXX Why?
	sys.argv = [sys.argv[0]]
	nose.run()

if __name__ == '__main__':
	main()
