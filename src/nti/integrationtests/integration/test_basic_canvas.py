import os
import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.utils import image_to_data_url
from nti.integrationtests.contenttypes import CanvasUrlShape
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

from hamcrest import (is_, is_not, assert_that)

class TestBasicCanvas(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicCanvas, self).setUp()
		
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)
		
	def test_creating_a_canvas(self):

		canvasAffineTransform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygonShape = CanvasPolygonShape(sides=4, transform=canvasAffineTransform, container=self.container)
		canvas = Canvas(shapeList=[polygonShape], container=self.container)
		created_obj = self.ds.create_object(canvas, adapt=True)
		
		assert_that(created_obj['id'], is_not(None))
		assert_that(created_obj['shapeList'][0]['sides'], is_(4))
		assert_that(created_obj['shapeList'][0]['transform']['a'], is_(0))
		assert_that(created_obj['shapeList'][0]['transform']['b'], is_(0))
		assert_that(created_obj['shapeList'][0]['transform']['c'], is_(0))
		assert_that(created_obj['shapeList'][0]['transform']['d'], is_(0))
		assert_that(created_obj['shapeList'][0]['transform']['tx'], is_(.25))
		assert_that(created_obj['shapeList'][0]['transform']['ty'], is_(.25))
		
	def test_canvas_and_image(self):

		source_file = os.path.join(os.path.dirname(__file__), "_class_image.jpg")
		url = image_to_data_url(source_file)
		urlShape = CanvasUrlShape(url=url)
		canvas = Canvas(shapeList=[urlShape], container=self.container)
		created_obj = self.ds.create_object(canvas, adapt=True)
		urlShape = created_obj.shapeList[0]
		assert_that(urlShape.url, is_not(None))
		
if __name__ == '__main__':
	unittest.main()