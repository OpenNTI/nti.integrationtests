from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

class Community(DSObject):
    
    DATASERVER_CLASS = 'Community'
    
    _ds_field_mapping = {'name': 'Username', 'alias':'alias', 'avatarURL':'avatarURL'}
    _ds_field_mapping.update(DSObject._ds_field_mapping)

    _fields = {'name': True, 'alias': False, 'avatarURL': False}
    _fields.update(DSObject._fields)
    
    def __getitem__(self, key):
        if key == 'Username' or key == 'username':
            key = 'name'
        return super(Community, self).__getitem__(key)
    
    def __setitem__(self, key, val):
        if key == 'name' or key == 'username' or key == 'Username':
            self._data[self._ds_field_mapping['name']] = val
        else:
            super(Community, self).__setitem__(key, val)
            
class FriendsList(Community):
    
    DATASERVER_CLASS = 'FriendsList'
    MIME_TYPE = 'application/vnd.nextthought.friendslist'
    
    _ds_field_mapping = {'friends' : 'friends'}
    _ds_field_mapping.update(Community._ds_field_mapping)

    _fields = {'friends' : False}
    _fields.update(Community._fields)

    def __setitem__(self, key, val):
        if key == 'friends':
            self._assign_to_list(self._ds_field_mapping['friends'], val)
        else:
            super(FriendsList, self).__setitem__(key, val)

class DynamicFriendsList(FriendsList):
    
    # DATASERVER_CLASS = 'DynamicFriendsList'
    MIME_TYPE = 'application/vnd.nextthought.dynamicfriendslist'
    
    _ds_field_mapping = {'creator':'creator', 'ntiid':'NTIID'}
    _ds_field_mapping.update(FriendsList._ds_field_mapping)

    _fields = {'creator':False, 'ntiid':False}
    _fields.update(FriendsList._fields)
            
class User(Community):
    
    DATASERVER_CLASS = 'User'
    
    _ds_field_mapping = {'communities': 'Communities', 'notificationCount':'NotificationCount', 
                         'presence':'Presence', 'lastLoginTime':'lastLoginTime', 'accepting':'accepting', 
                         'following': 'following', 'ignoring':'ignoring', 'realname':'realname' }
    _ds_field_mapping.update(Community._ds_field_mapping)

    _fields = { 'communities' : False, 'notificationCount':True, 'presence':True, 'lastLoginTime':False,
                'accepting': False, 'following': False, 'ignoring':False, 'realname': False }
    _fields.update(Community._fields)

    def __getitem__(self, key):
        if key == 'notificationCount' or key == 'NotificationCount':
            key = 'notificationCount'
        return super(User, self).__getitem__(key)
    
    def __setitem__(self, key, val):
        if key == 'communities' or key == 'Communities':
            self._assign_to_list(self._ds_field_mapping['communities'], val)
        elif key == 'accepting':
            self._assign_to_list(self._ds_field_mapping['accepting'], val)
        elif key == 'ignoring':
            self._assign_to_list(self._ds_field_mapping['ignoring'], val)
        else:
            super(User, self).__setitem__(key, val)


do_register_dsobjecs((Community, FriendsList, DynamicFriendsList, User))

