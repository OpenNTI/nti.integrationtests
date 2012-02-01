import time
import unittest

from hamcrest import assert_that
from hamcrest import is_not
from hamcrest import is_

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

class TestBasicNotes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)
	string = 'a note to post'

	def setUp(self):
		super(TestBasicNotes, self).setUp()
		
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)

# ----------------------

	# tests the five different types of notes that can be made
	
	def test_create_note_with_string(self):
		# create the object to share
		created_obj =  self.ds.create_note(self.string, self.container, adapt=True)
		
		# asserts that the object created has the string
		assert_that(created_obj['body'][0], is_('a note to post'))
	
	def test_create_note_with_string_in_array(self):
		
		# create the object to share
		created_obj =  self.ds.create_note([self.string], self.container, adapt=True)
		
		# asserts that the object created has the string
		assert_that(created_obj['body'][0], is_('a note to post'))
		
	def test_create_note_with_string_and_object_in_array(self):
		
		created_canvas = self.create_canvas()
		
		# create the objec to share
		created_obj =  self.ds.create_note([self.string, created_canvas], self.container, adapt=True)
		
		# asserts that the object created has a canvas object and the string
		assert_that(created_obj['body'][0], is_('a note to post'))
		assert_that(created_obj['body'][1], is_(Canvas))
		
	def test_create_note_with_object_in_array(self):
		
		created_canvas = self.create_canvas()
		
		# create the object to share
		created_obj =  self.ds.create_note([created_canvas], self.container, adapt=True)
		
		# asserts that the object created has a canvas object
		assert_that(created_obj['body'][0], is_(Canvas))

	def test_create_note_with_object(self):
		
		created_canvas = self.create_canvas()
		
		# create the object to share
		created_obj =  self.ds.create_note(created_canvas, self.container, adapt=True)
		
		# asserts that the object created has a canvas object
		assert_that(created_obj['body'][0], is_(Canvas))

# ----------------------

	def create_canvas(self):
		
		# creates a canvas
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		return self.ds.create_object(canvas, adapt=True)

	createCanvas = create_canvas
	
# ----------------------

	def test_body_key_is_object(self):
		# create the object to share
		created_obj =  self.ds.create_note('A note to post', self.container, adapt=True)
		
		# asserts that the shared object contains none.
		assert_that(created_obj['body'][0]), is_("A reply to note")
		assert_that(created_obj['inReplyTo'], is_(None))
		assert_that(created_obj['references'], is_(None))
		assert_that(created_obj['id'], is_not(None))
		
	def test_storing_object_in_body(self):
		
		# create the object to share
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		created_obj = self.ds.create_object(canvas, adapt=True)
		
		created_note = self.ds.create_note([created_obj], self.container, adapt=True)
		assert_that(created_note['body'][0]['container'], is_(created_obj['container']))
		assert_that(created_obj['id'], is_not(None))
		
	def test_storing_text_and_object_in_body(self):
		
		# create the object to share
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		created_obj = self.ds.create_object(canvas, adapt=True)
		
		created_note = self.ds.create_note(['check this out' , created_obj], self.container, adapt=True)
		assert_that(created_note['body'][1]['container'], is_(created_obj['container']))
		assert_that(created_obj['id'], is_not(None))

if __name__ == '__main__':
	unittest.main()