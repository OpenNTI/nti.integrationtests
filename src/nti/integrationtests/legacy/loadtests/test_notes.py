import os
import time
import random
import socket
import unittest
import collections
import multiprocessing

from concurrent.futures import ThreadPoolExecutor
from nti.integrationtests.legacy.loadtests import new_client, post_note, generate_message, ENDPOINT

from hamcrest import (assert_that, is_, has_key, has_length)

# ---------------------------

host_name = socket.gethostname()

# ---------------------------

def post_random_notes(user, 
					  container=None,
					  max_notes=None,
					  max_time=None,
					  post_delay=0.25,
					  endpoint=ENDPOINT,
					  on_posted_note_callback=None):
	
	assert max_notes or max_time
	
	client = new_client(user=user, endpoint=endpoint)
	container = container or '%s.%s.%s' % (host_name, user, time.time())
	
	t = time.time()
	elpased_time = 0
	note_counter = 0
	
	posted = 0
	failed = 0
	notes = []
	
	while (max_notes and note_counter < max_notes) or (max_time and elpased_time < max_time):
		t = time.time()
		
		message = "[ %s ]: %s" % (user.replace('.','-'), generate_message()) 
		note = post_note (client, container, message)
		if note:
			if on_posted_note_callback:
				obj = on_posted_note_callback(client, user, container, note)
				if obj:
					posted = posted + 1
					if (obj.__class__ == note.__class__):
						note = obj
				else:
					failed = failed + 1
					note = None
			else:
				posted = posted + 1
				
			if note:
				notes.append(note)
		else:
			failed = failed + 1
		
		if post_delay:
			time.sleep(post_delay)
			
		note_counter = note_counter + 1
		elpased_time = elpased_time + (time.time() - t)

	return (user, container, notes, posted, failed)
	
	
def post_notes_for_users(max_users=None,
						 max_notes=None,
						 max_time=None, 
						 min_post_delay=0,
						 max_post_delay=0.25, 
						 endpoint=ENDPOINT,
						 on_posted_note_callback=None):
	
	max_users = max_users or multiprocessing.cpu_count()
	
	futures = []
	with ThreadPoolExecutor(multiprocessing.cpu_count()) as pool:
		for x in range(1, max_users+1):
			name = 'test.user.%s@nextthought.com' % x
			container = '%s.container.%s' % (name, time.time())
			
			post_delay = random.uniform(min_post_delay, max_post_delay) \
						 if min_post_delay and max_post_delay else 0.25

			futures.append(pool.submit(	post_random_notes,
										user = name, 
										container = container,
										max_notes=max_notes, 
										max_time=max_time, 
										post_delay=post_delay,
										endpoint=endpoint,
										on_posted_note_callback=on_posted_note_callback) )
			
	result = []
	for f in futures:
		result.append(f.result())
	
	return result


def post_notes_and_share(max_users=None,
						 max_notes=None,
						 max_time=None, 
						 min_post_delay=0,
						 max_post_delay=0.25, 
						 endpoint=ENDPOINT):
	
	users = ['test.user.%s@nextthought.com' % x for x in range(1, max_users+1)]
	
	def on_posted_note(client, user, container, note):
		s = set(users)
		s.remove(user)
		try:
			return client.shareObject(note, list(s), adapt=True)
		except:
			pass
		return None
	
	return post_notes_for_users(max_users=max_users,
						 		max_notes=max_notes,
						 		max_time=max_time, 
						 		min_post_delay=min_post_delay,
						 		max_post_delay=max_post_delay, 
						 		endpoint=endpoint,
						 		on_posted_note_callback=on_posted_note)

def post_notes_and_delete(max_users=None,
						  max_notes=None,
						  max_time=None, 
						  min_post_delay=0,
						  max_post_delay=0.25, 
						  endpoint=ENDPOINT):
	
	deleted = collections.defaultdict(list)
	
	def on_posted_note(client, user, container, note):
		if random.random() >= 0.5:
			try:
				client.deleteObject(note, adapt=True)
				deleted[user].append(note.id)
			except:
				return False
		return True
	
	futures_r = post_notes_for_users(max_users=max_users,
									 max_notes=max_notes,
						 			max_time=max_time, 
						 			min_post_delay=min_post_delay,
						 			max_post_delay=max_post_delay, 
						 			endpoint=endpoint,
						 			on_posted_note_callback=on_posted_note)
	
	return (futures_r, deleted)


def post_notes_and_update(max_users=None,
						  max_notes=None,
						  max_time=None, 
						  min_post_delay=0,
						  max_post_delay=0.25, 
						  endpoint=ENDPOINT):
	
	updated = collections.defaultdict(dict)
	
	def on_posted_note(client, user, container, note):
		if random.random() >= 0.4:
			old_message = note['body']
			try:
				new_message = "[ %s ]: %s" % (user.replace('.','-'), generate_message()) 
				note['body'] = [new_message]
				updated_obj = client.updateObject(note)
				updated[user][updated_obj.id] = updated_obj
			except:
				return False
			finally:
				note['body'] = old_message
		return True
	
	futures_r = post_notes_for_users(max_users=max_users,
									 max_notes=max_notes,
						 			max_time=max_time, 
						 			min_post_delay=min_post_delay,
						 			max_post_delay=max_post_delay, 
						 			endpoint=endpoint,
						 			on_posted_note_callback=on_posted_note)
	
	return (futures_r, updated)

# ---------------------------

_server_end_point = os.environ['ENDPOINT'] if 'ENDPOINT' in os.environ else ENDPOINT
_min_post_delay = float(os.environ['MIN_POST_DELAY']) if 'MIN_POST_DELAY' in os.environ else 0.25
_max_post_delay = float(os.environ['MAX_POST_DELAY']) if 'MAX_POST_DELAY' in os.environ else 1.5
_max_notes_to_post = int(os.environ['MAX_NOTES_TO_POST']) if 'MAX_NOTES_TO_POST' in os.environ else 500
_max_users = int(os.environ['MAX_USERS']) if 'MAX_USERS' in os.environ else multiprocessing.cpu_count()

class TestNotes(unittest.TestCase):
	
	@unittest.SkipTest
	def test_post_random_notes(self):
		
		expected_notes = _max_notes_to_post
		
		result = post_notes_for_users(max_users = _max_users,
									  max_notes = expected_notes,
									  min_post_delay = _min_post_delay,
							 		  max_post_delay = _max_post_delay,
							 		  endpoint = _server_end_point)
		for t in result:
			user, container, _, posted, failed = t
			assert_that(failed, is_(0) )
			assert_that(posted, is_(expected_notes))
			
			client = new_client(user=user, endpoint=_server_end_point)
			data = client.getUserGeneratedData(container)
			assert_that(data, has_key('Items'))
			assert_that(data['Items'], has_length(expected_notes))
	
	@unittest.SkipTest
	def test_post_and_share_notes(self):
		
		expected_notes = _max_notes_to_post
		
		result = post_notes_and_share(max_users = _max_users,
									  max_notes = expected_notes,
									  min_post_delay = _min_post_delay,
							 		  max_post_delay = _max_post_delay,
							 		  endpoint = _server_end_point)
		for t in result:
			user, container, _, posted, failed = t
			assert_that(failed, is_(0) )
			assert_that(posted, is_(expected_notes))
			
			client = new_client(user=user, endpoint=_server_end_point)
			data = client.getUserGeneratedData(container)
			assert_that(data, has_key('Items'))
			assert_that(data['Items'], has_length(expected_notes))	
			
	@unittest.SkipTest
	def test_post_and_delete_notes(self):
		
		expected_notes = _max_notes_to_post
		
		result, deleted = post_notes_and_delete(max_users = _max_users,
												max_notes = expected_notes,
												min_post_delay = _min_post_delay,
							 					max_post_delay = _max_post_delay,
							 					endpoint = _server_end_point)
		
		for t in result:
			user, container, _, posted, failed = t
			assert_that(failed, is_(0) )
			assert_that(posted, is_(expected_notes))
			
			client = new_client(user=user, endpoint=_server_end_point)
			data = client.getUserGeneratedData(container)
			assert_that(data, has_key('Items'))
			
			ud = deleted[user]
			items = data['Items']
			assert_that(items, has_length(expected_notes - len(ud)))	
			
	def test_post_notes_and_update(self):
		
		expected_notes = _max_notes_to_post
		
		result, updated = post_notes_and_update(max_users = _max_users,
												max_notes = expected_notes,
												min_post_delay = _min_post_delay,
							 					max_post_delay = _max_post_delay,
							 					endpoint = _server_end_point)
		for t in result:
			user, container, _, posted, failed = t
			assert_that(failed, is_(0) )
			assert_that(posted, is_(expected_notes))
			
			client = new_client(user=user, endpoint=_server_end_point)
			data = client.getUserGeneratedData(container)
			assert_that(data, has_key('Items'))
			assert_that(data['Items'], has_length(expected_notes))
			
			for item in data['Items']:
				if item.creator in updated and item.id in updated[item.creator]:
					assert_that(item['body'], is_(updated[item.creator][item.id]['body']))
			
if __name__ == '__main__':
	unittest.main()
	
