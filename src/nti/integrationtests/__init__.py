import time
import uuid
import random
import numbers
import unittest
import datetime
import collections

from nti.integrationtests.utils import PORT
from nti.integrationtests.utils import get_open_port
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.dataserver.client import ROOT_ITEM
from nti.integrationtests.utils import DEFAULT_USER_PASSWORD
from nti.integrationtests.dataserver.server import DATASERVER_DIR
from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.dataserver.client import DataserverClient

# When invoked through runners/__init__.py, these setup methods seem to get called twice
# for no reason that's entirely clear. So make them idempotent.
# (That module handles the actual setup and teardown anyway)
def setup_package():
	if DataServerTestCase.start_server():
		time.sleep(5)

def teardown_package():
	if DataServerTestCase.process is not None:
		DataServerTestCase.process.terminate_server()
		DataServerTestCase.process = None

class DataServerTestCase(unittest.TestCase):

	# well-known IDs

	DATE = "2011-10"
	ROOT = "tag:nextthought.com,2011-10:Root"

	TYPE_OID = 'OID'

	TYPE_ROOM = 'MeetingRoom'
	TYPE_MEETINGROOM = TYPE_ROOM

	TYPE_HTML = 'HTML'
	TYPE_QUIZ = 'Quiz'

	TYPE_CLASS = 'Class'
	TYPE_CLASS_SECTION = 'ClassSection'

	TYPE_MEETINGROOM_GROUP = TYPE_ROOM + ':Group'
	TYPE_MEETINGROOM_CLASS = TYPE_ROOM + ':Class'
	TYPE_MEETINGROOM_SECT  = TYPE_ROOM + ':ClassSection'
	TYPE_TRANSCRIPT = 'Transcript'
	TYPE_TRANSCRIPT_SUMMARY = 'TranscriptSummary'

	# class vars

	port = PORT
	root_dir = DATASERVER_DIR

	user_names = []
	root_item = ROOT_ITEM

	headers = None
	op_delay = None
	default_user_password = DEFAULT_USER_PASSWORD

	# We need to start a dataserver (and stop it)
	# if there is not already one running
	@classmethod
	def setUpClass(cls):
		cls.static_initialization()

	@classmethod
	def tearDownClass(cls):
		cls.static_finalization()

	def setUp(self):
		self.ds = self.create_client()

	@property
	def client(self):
		return self.ds

	def create_client(self, headers=None, op_delay=None):
		endpoint = self.get_endpoint()
		headers = headers or self.headers
		op_delay = op_delay or self.op_delay
		result = self.new_client(endpoint=endpoint, headers=headers, op_delay=op_delay)
		return result

	def get_endpoint(self):
		if hasattr(self, 'endpoint'):
			return self.endpoint
		return self.resolve_endpoint(port = self.port)

	@classmethod
	def resolve_endpoint(cls, host=None, port=None):
		return DataserverProcess.resolve_endpoint(host, port)

	@classmethod
	def new_client(cls, credentials=None, endpoint=None, headers=None, op_delay=None):
		endpoint = endpoint or DataserverProcess.ENDPOINT2
		clt = DataserverClient(endpoint=endpoint, headers=headers, op_delay=op_delay)
		if credentials:
			clt.set_credentials(credentials)
		return clt

	# ======================

	process = None

	@classmethod
	def start_server(cls):
		if cls.process is None:
			cls.process = DataserverProcess(port=cls.port, root_dir=cls.root_dir)
			cls.process.start_server()
			return True

	@classmethod
	def static_initialization(cls):
		pass

	@classmethod
	def static_finalization(cls):
		pass

	@classmethod
	def generate_ntiid(cls, date=None, provider='nti', nttype=None, specific=None):
		return generate_ntiid(date=date, provider=provider, nttype=nttype, specific=specific)
