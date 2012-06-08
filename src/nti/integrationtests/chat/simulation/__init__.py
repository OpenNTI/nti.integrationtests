import uuid

from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD

from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import Invitee
from nti.integrationtests.chat.objects import run_chat

MAX_TEST_USERS = 100

def create_friends_list(username, friends, list_name=None, server='localhost', port=8081, is_secure=False,
                        password=DEFAULT_USER_PASSWORD):
    
    password = password or DEFAULT_USER_PASSWORD
    endpoint = DataserverProcess.resolve_endpoint(server, port, is_secure)
    ds = DataserverClient(endpoint=endpoint, credentials=(username, DEFAULT_USER_PASSWORD))
    list_name = list_name or 'cfl-%s' % str(uuid.uuid4())
            
    # prepare friends 
    users = set(friends)
    users.remove(username)
    
    # create friends list
    ds.create_friends_list_with_name_and_friends(list_name, sorted(users))
    
def create_test_friends_lists(users, server='localhost', port=8081, is_secure=False, start_user=1, for_all=False):
    host = 'test.user.%s@nextthought.com' % start_user
    users =['test.user.%s@nextthought.com' % s for s in range(start_user+1, users+start_user)]
    if for_all:
        all_users = [host] + users
        for username in all_users:
            create_friends_list(username, all_users, server=server, port=port, is_secure=is_secure)
    else:
        create_friends_list(host, users, server=server, port=port, is_secure=is_secure)
        
def simulate(users, containerId, entries=None, delay=2, server='localhost', port=8081,
             max_heart_beats=3, use_threads=True, host_class=Host, invitee_class=Invitee,
             create_test_lists=False, is_secure=False, start_user=1):
    
    users = max(min(abs(users), MAX_TEST_USERS), 2)
    entries = abs(entries) if entries else 50
            
    if create_test_lists:
        create_test_friends_lists(users, server, port, is_secure, start_user=start_user)
        
    host = 'test.user.1@nextthought.com'
    users =['test.user.%s@nextthought.com' % s for s in range(2, users+1)]
    
    result = run_chat(containerId, host, users, entries=entries, delay=delay,
                      use_threads=use_threads, server=server, port=port,
                      max_heart_beats=max_heart_beats, host_class=host_class,
                      invitee_class=Invitee, is_secure=is_secure, start_user=start_user)
    
    return result