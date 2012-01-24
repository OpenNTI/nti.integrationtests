'''
Created on Jan 13, 2012

@author: ltesti
'''

from servertests.serverfunctionality.utils import USERNAME, PASSWORD, URL, DATASERVER
from servertests.serverfunctionality.utils.generaterequest import ServerRequest
from servertests.serverfunctionality.utils.serverdata import Workspace
from servertests import DataServerTestCase

from servertests.serverfunctionality.utils.url_formatter import NoFormat
from servertests.serverfunctionality.utils.url_formatter import JsonFormat
from servertests.serverfunctionality.utils.url_formatter import PlistFormat

from servertests.serverfunctionality.utils.post_runner import PostObject
from servertests.serverfunctionality.utils.get_runner import GetObject
from servertests.serverfunctionality.utils.get_collection_runner import GetGroupObject
from servertests.serverfunctionality.utils.put_runner import PutObject
from servertests.serverfunctionality.utils.delete_runner import DeleteObject

from servertests.serverfunctionality.utils.request_types import Successful
from servertests.serverfunctionality.utils.request_types import Unauthorized
from servertests.serverfunctionality.utils.request_types import NotFound
from servertests.serverfunctionality.utils.request_types import BadData

from servertests.serverfunctionality.tests import NoteTest
from servertests.serverfunctionality.tests import HighlightTest
from servertests.serverfunctionality.tests import FriendsListTest
from servertests.serverfunctionality.tests import CanvasTest
from servertests.serverfunctionality.tests import CanvasShapeTest
from servertests.serverfunctionality.tests import CanvasCircleShapeTest
from servertests.serverfunctionality.tests import CanvasPolygonShapeTest


def setup():
	DataServerTestCase.setUpClass()
	
def teardown():
	DataServerTestCase.tearDownClass()
	
def run_tests():
	noFormat = NoFormat()
	requests = ServerRequest()
	
	dataserverURL = URL + DATASERVER
	serverDocRequest = requests.get(url=dataserverURL, username=USERNAME, password=PASSWORD)
	parsedBody = noFormat.read(serverDocRequest)
	workspace = Workspace.new_from_dict(parsedBody['Items'][0])
	
	REQUEST_TYPES = [PostObject(), GetObject(), GetGroupObject(), PutObject(), DeleteObject()]
	RESPONSE_TYPES = [Successful(), Unauthorized(), NotFound(), BadData()]
	TEST_TYPES = [NoteTest(), HighlightTest(), FriendsListTest(), CanvasTest(), CanvasShapeTest(), CanvasCircleShapeTest(), CanvasPolygonShapeTest()]
	FORMATS = [NoFormat(), JsonFormat(), PlistFormat()]
	
	for collection in workspace.collections:
		href = workspace.collections[collection].href
		for accept in workspace.collections[collection].accepts:
			for test_type in TEST_TYPES:
				if test_type.TYPE == accept:
					if test_type.IS_OBJ == True: requests = REQUEST_TYPES
					else: requests = [REQUEST_TYPES[0]]
					for request in requests:
						for responseType in RESPONSE_TYPES:
							for formatt in FORMATS:
								kwargs = {'href':href, 'objRunner':test_type, 'responseType':responseType, 'format':formatt}
								if request is REQUEST_TYPES[0] and responseType is RESPONSE_TYPES[2]: pass
								elif test_type.IS_OBJ is True and request is not REQUEST_TYPES[0] and request is not REQUEST_TYPES[3] and responseType is RESPONSE_TYPES[3]: pass
								else: yield request.makeRequest, kwargs
						