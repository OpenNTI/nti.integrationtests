import unittest

from nti.integrationtests.integration import test_friends_lists

class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists):
	isDynamic = True
	
if __name__ == '__main__':
	unittest.main()
