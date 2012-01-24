import time
import random
import unittest
	
import gevent
import greenlet

from servertests import DataServerTestCase

phrases = (	"Yellow brown", "Blue red green render purple?",\
			"Alpha beta", "Gamma delta epsilon omega.",\
			"One two", "Three rendered four five.",\
			"Quick went", "Every red town.",\
			"Yellow uptown",  "Interest rendering outer photo!",\
			"Preserving extreme", "Chicken hacker")

@unittest.SkipTest
class TestStressTests(DataServerTestCase):
	
	def generate_message(self, aMin=2, aMax=5):
		return " ".join(random.sample(phrases, random.randint(aMin, aMax)))
	
	def test_random_notes(self):
		
		jobs = []
		container = 'test.user.container.%s' % time.time()

		parent_greenlet = greenlet.getcurrent()
		
		def post_random_notes(user, notes, container, interval=4):
			count = 0
			client = DataServerTestCase.new_client((user, self.default_user_password))
			for _ in range(0, notes):
				text = self.generate_message(2, 5)
				try:
					client.create_note(text, container, adapt=True)
					count = count + 1
					gnext = random.randint(0, len(jobs))
					if greenlet.getcurrent() != jobs[gnext]:
						jobs[gnext].switch()
				except:
					pass
		
			jobs.remove(greenlet.getcurrent())
			parent_greenlet.switch()
			
		nusers = random.randint(10, 50)
		print 'Start with %s users' % nusers
		
		for i in range(0, nusers):
						
			job = gevent.Greenlet.spawn(post_random_notes,
											user = "test.user.%s@nextthought.com" % i,
											notes= random.randint(1, 30),
											container = container)
			
			jobs.append(job)
				
		while jobs:
			gnext = random.randint(0, len(jobs))
			if gnext < len(jobs):
				jobs[gnext].switch()
	
		print 'end'
			
if __name__ == '__main__':
	unittest.main()
	