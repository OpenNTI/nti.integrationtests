from __future__ import print_function, unicode_literals

import time
import uuid
import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.chat.simulation import MAX_TEST_USERS

from hamcrest import (assert_that, is_not)

_max_users = MAX_TEST_USERS

import logging
logger = logging.getLogger(__name__)

def _wait(context):
	min_delay = context.as_float('min_delay', 0)
	max_delay = context.as_float('max_delay', 0)
	delay = random.uniform(min_delay, max_delay)
	if delay > 0:
		time.sleep(delay)
		
def create(**kwargs):
	context = kwargs['__context__']
	client = new_client(context)
	
	c = chr(random.randint(ord('a'), ord('z')))
	code =  unicode(uuid.uuid4()).split('-')[0]
	username = unicode(c + code) + '@nextthought.com'
	email = username
	password = 'temp001'
	realname = username
	opt_in_email_communication = random.random() >= 0.5
	
	user_object = client.create_user(username, password, email, realname, opt_in_email_communication)
	assert_that(user_object, is_not(None))
	
	_wait(context)
	
	return IGNORE_RESULT

