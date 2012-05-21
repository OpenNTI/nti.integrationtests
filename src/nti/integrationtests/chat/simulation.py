#!/usr/bin/env python

import uuid

from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD

from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import Invitee
from nti.integrationtests.chat.objects import run_chat

def create_friends_list(username, friends, list_name=None, server='localhost', port=8081, is_secure=False,
                        password=DEFAULT_USER_PASSWORD):
    
    password = password or DEFAULT_USER_PASSWORD
    endpoint = DataserverProcess.resolve_endpoint(server, port, is_secure)
    ds = DataserverClient(endpoint=endpoint, credentials=(username, DEFAULT_USER_PASSWORD))
    list_name = list_name or 'cfl-%s-%s' % (username, str(uuid.uuid4()).split('-')[0])
            
    # prepare friends 
    users = set(friends)
    users.remove(username)
    
    # create friends list
    ds.create_friends_list_with_name_and_friends(list_name, list(users))
    
def create_test_friends_lists(users, server='localhost', port=8081, is_secure=False):
    host = 'test.user.1@nextthought.com'
    users =['test.user.%s@nextthought.com' % s for s in range(2, users+1)]
    all_users = [host] + users
    for username in all_users:
        create_friends_list(username, all_users, server=server, port=port, is_secure=is_secure)
        
def simulate(users, containerId, entries=None, delay=2, server='localhost', port=8081,
             max_heart_beats=3, use_threads=True, host_class=Host, invitee_class=Invitee,
             create_test_lists=True, is_secure=False):
    
    users = max(min(abs(users), 50), 2)
    entries = abs(entries) if entries else 50
            
    if create_test_lists:
        create_test_friends_lists(users, server, port, is_secure)
        
    host = 'test.user.1@nextthought.com'
    users =['test.user.%s@nextthought.com' % s for s in range(2, users+1)]
    
    result = run_chat(containerId, host, users, entries=entries, delay=delay,
                      use_threads=use_threads, server=server, port=port,
                      max_heart_beats=max_heart_beats, host_class=host_class,
                      invitee_class=Invitee )
    
    return result

if __name__ == '__main__':
    result = simulate(2, 'tag:nextthought.com,2011-10:AOPS-HTML-prealgebra.0', 3,
                      server='alpha.nextthought.com', port=443, is_secure=True)
    
    for r in result:
        print r.username, len(list(r.sent)), len(list(r.received)), r.traceback
