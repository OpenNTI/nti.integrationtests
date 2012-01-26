"""
Created on Dec 21, 2011

@author: ltesti
"""

import os
from servertests import DataserverProcess

findPort = DataserverProcess()

PORT = os.getenv('PORT', str(findPort.PORT))
URL = os.getenv('URL', "http://localhost:" + PORT)
ACCEPTS = os.getenv('ACCEPTS', 'application/vnd.nextthought.')
DATASERVER = os.getenv('DATASERVER', "/dataserver2/")
TEMPUSER = os.getenv('TEMPUSER', 'logan.testi')
USERNAME = os.getenv('USERNAME', TEMPUSER + "@nextthought.com")
PASSWORD = os.getenv('PASSWORD', TEMPUSER)
PATH_TO_TESTS = os.getenv('PATH_TO_TESTS', os.path.dirname(__file__) +'/../testtypes/')