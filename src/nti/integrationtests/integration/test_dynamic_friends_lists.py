import uuid
import unittest

from nti.integrationtests.integration import test_friends_lists
from nti.integrationtests.integration import test_friends_sharing

class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists,
							  test_friends_sharing.TestFriendsSharing):
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()		
		self.realname ='%s@nt.com' % str(uuid.uuid4()).split('-')[-1]
		
	def create_friends_list_with_name_and_friends(self, name, friends):
		dfl = self.ds.create_DFL_with_name_and_friends(name, friends, realname=self.realname)
		return dfl
	
if __name__ == '__main__':
	unittest.main()
