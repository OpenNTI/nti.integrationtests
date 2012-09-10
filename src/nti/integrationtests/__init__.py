import time
import uuid
import random
import numbers
import unittest
import datetime
import collections

from nti.integrationtests.utils import get_open_port
from nti.integrationtests.dataserver.server import PORT
from nti.integrationtests.dataserver.server import DATASERVER_DIR
from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.client import ROOT_ITEM

import nti.dataserver # Gevent monkey patches

def generate_ntiid(date=None, provider='nti', nttype=None, specific=None):

	def escape_provider( provider ):
		return provider.replace( ' ', '_' ).replace( '-', '_' )

	if not nttype:
		raise ValueError( 'Must supply type' )

	date_seconds = date if isinstance( date, numbers.Real ) and date > 0 else time.time()
	date = datetime.date( *time.gmtime(date_seconds)[0:3] )
	date_string = date.isoformat()

	provider = escape_provider( str(provider) ) + '-'
	specific = '-' + specific if specific else '-' + str(time.clock())

	result = 'tag:nextthought.com,%s:%s%s%s' % (date_string, provider, nttype, specific )
	return result


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

	default_user_password = DEFAULT_USER_PASSWORD

	# We need to start a dataserver (and stop it)
	# if there is not already one running
	@classmethod
	def setUpClass(cls):
		cls.static_initialization()

	def setUp(self):
		endpoint = self.get_endpoint()
		self.ds = DataserverClient(endpoint)

	@property
	def client(self):
		return self.ds

	def get_endpoint(self):
		if hasattr(self, 'endpoint'):
			return self.endpoint
		return self.resolve_endpoint(port = self.port)

	# ======================

	@classmethod
	def resolve_endpoint(cls, host=None, port=None):
		return DataserverProcess.resolve_endpoint(host, port)

	@classmethod
	def new_client(cls, credentials=None, endpoint=None):
		clt = DataserverClient(endpoint or DataserverProcess.ENDPOINT2)
		if credentials:
			clt.set_credentials(credentials)
		return clt

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
	def generate_ntiid(cls, date=None, provider='nti', nttype=None, specific=None):
		return generate_ntiid(date=date, provider=provider, nttype=nttype, specific=specific)
