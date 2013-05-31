from __future__ import print_function, unicode_literals

import time
import random

from nti.integrationtests.performance import IGNORE_RESULT
from nti.integrationtests.utils import generate_random_text
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
		
def search(**kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']

	idx = runner % _max_users
	username = "test.user.%s" % idx
	credentials = ("%s@nextthought.com" % username, 'temp001')
	client = new_client(context)
	client.set_credentials(credentials)
	
	exact_match_percentage = context.as_float('exact_match_percentage', 0.5)
	if random.random() >= exact_match_percentage:
		query = username
	else:
		min_qz = context.as_int('min_query_size', 3)
		max_qz = context.as_int('max_query_size', 5)
		query_size = random.randint(min_qz, max_qz)
		query = generate_random_text(query_size)
		
	users = client.execute_user_search(query)
	assert_that(users, is_not(None))
	
	_wait(context)
	
	return IGNORE_RESULT

def resolve(**kwargs):
	context = kwargs['__context__']
	runner = kwargs['__runner__']
	
	idx = runner % _max_users
	username = "test.user.%s@nextthought.com" % idx
	credentials = (username, 'temp001')
	client = new_client(context)
	client.set_credentials(credentials)
	
	exact_match_percentage = context.as_float('exact_match_percentage', 0.5)
	if random.random() >= exact_match_percentage:
		query = username
	else:
		min_qz = context.as_int('min_query_size', 3)
		max_qz = context.as_int('max_query_size', 5)
		query_size = random.randint(min_qz, max_qz)
		query = generate_random_text(query_size)
		
	users = client.resolve_user(query)
	assert_that(users, is_not(None))
	
	_wait(context)
		
	return IGNORE_RESULT
