import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.contenttypes.users import DynamicFriendsList

from nti.integrationtests.integration import test_friends_lists
from hamcrest import (is_not, assert_that)

@unittest.SkipTest
class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists):
	isDynamic = True
	
if __name__ == '__main__':
	unittest.main()
