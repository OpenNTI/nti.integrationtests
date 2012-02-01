import os

from nti.integrationtests.dataserver.server import PORT as SERVER_PORT

PORT = os.getenv('PORT', str(SERVER_PORT))
URL = os.getenv('URL', "http://localhost:" + PORT)
ACCEPTS = os.getenv('ACCEPTS', 'application/vnd.nextthought.')
DATASERVER = os.getenv('DATASERVER', "/dataserver2/")
TEMPUSER = os.getenv('TEMPUSER', 'logan.testi')
USERNAME = os.getenv('USERNAME', TEMPUSER + "@nextthought.com")
PASSWORD = os.getenv('PASSWORD', TEMPUSER)
PATH_TO_TESTS = os.getenv('PATH_TO_TESTS', os.path.dirname(__file__) +'/../testtypes/')