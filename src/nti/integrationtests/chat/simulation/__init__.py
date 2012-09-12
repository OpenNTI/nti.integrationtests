import os
import sys
import time
import uuid
import pprint

from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import Invitee
from nti.integrationtests.chat.objects import run_chat
from nti.integrationtests.utils import DEFAULT_USER_PASSWORD
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import DataserverProcess

MAX_TEST_USERS = 100

def wait_and_process(self, delay, condf=lambda : True):
    elapsed = 0
    while elapsed < delay and condf():
        t = time.time()
        self.nextEvent() # process any message while waiting
        t = max(time.time() - t, 0.01)
        elapsed = elapsed + t
    return elapsed
        
def pprint_to_file(self, outdir=None, full=False, **kwargs):
    outdir = os.path.expanduser(outdir or '/tmp')
    outname = os.path.join(outdir, self.username + ".txt")
    with open(outname, "w") as s:
        pprint_graph(self, stream=s, full=full, **kwargs)
    
def pprint_graph(self, lock=None, stream=None, full=False, **kwargs):
    stream = stream or sys.stderr
    try:
        if lock: lock.acquire()
        
        def get_messages(messages, is_recv=True):
            result = []
            result.append(len(messages))
            for m in messages:
                t = (m.ID or '', m.creator, m.text) if is_recv else m.text
                result.append(t)
            return result
        
        if full:
            _sent = get_messages(self.get_sent_messages(), False)
            _recv = get_messages(self.get_received_messages())
            _mode = get_messages(self.get_moderated_messages())
        else:
            _sent = len(list(self.sent))
            _recv = len(list(self.received))
            _mode = len(list(self.moderated))
            
        d = {'username' : self.username,
             'sent' : _sent,
             'received': _recv,
             'moderated':_mode,
             'elapsed_recv': self.elapsed_recv,
             'traceback': self.traceback,
             'params' : kwargs }
            
        pprint.pprint(d, stream=stream, indent=2)
    finally:
        if lock: lock.release()
    
def create_friends_list(username, friends, list_name=None, server='localhost', port=8081, is_secure=False,
                        password=DEFAULT_USER_PASSWORD):
    
    password = password or DEFAULT_USER_PASSWORD
    endpoint = DataserverProcess.resolve_endpoint(server, port, is_secure)
    ds = DataserverClient(endpoint=endpoint, credentials=(username, DEFAULT_USER_PASSWORD))
    list_name = list_name or 'cfl-%s' % str(uuid.uuid4())
            
    # prepare friends 
    users = set(friends)
    if username in users:
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
