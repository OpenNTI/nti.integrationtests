'''
Created on Jan 13, 2012

@author: ltesti
'''

import os
import json

from servertests.serverfunctionality.utils.response_assert import NoteBodyTester
from servertests.serverfunctionality.utils.response_assert import HighlightBodyTester
from servertests.serverfunctionality.utils.response_assert import FriendsListBodyTester
from servertests.serverfunctionality.utils.response_assert import CanvasBodyTester
from servertests.serverfunctionality.utils.response_assert import CanvasShapeBodyTester
from servertests.serverfunctionality.utils.response_assert import CanvasPolygonShapeBodyTester

from servertests.serverfunctionality.utils import ACCEPTS

def readObject(objFileName):
	tf = os.path.dirname(__file__) + '/../objects/' + objFileName
	with open(tf, "r") as f:
		obj = json.load(f)
		return obj
	
def readResponseValues(responseFileName):
	tf = os.path.dirname(__file__) + '/../expectedresponse/' + responseFileName
	with open(tf, "r") as f:
		response = json.load(f)
		return response

class NoteTest(object):
	
	TYPE = ACCEPTS + 'note'
	IS_OBJ = True
	
	@property
	def setup_obj(self):
		return 'setup_note.json'
	
	@property
	def test_obj(self):
		return 'test_note.json'
	
	@property
	def response_value(self):
		return 'note_response.json'
	
	@property
	def body_tester(self):
		return NoteBodyTester()
		
class HighlightTest(object):
	
	TYPE = ACCEPTS + 'highlight'
	IS_OBJ = True
	
	@property
	def setup_obj(self):
		return 'setup_highlight.json'
	
	@property
	def test_obj(self):
		return 'test_highlight.json'
	
	@property
	def response_value(self):
		return 'highlight_response.json'
	
	@property
	def body_tester(self):
		return HighlightBodyTester()
		
class FriendsListTest(object):
	
	TYPE = ACCEPTS + 'friendslist'
	IS_OBJ = True
	
	@property
	def setup_obj(self):
		return 'setup_friendslist.json'
	
	@property
	def test_obj(self):
		return 'test_friendslist.json'
	
	@property
	def response_value(self):
		return 'friendslist_response.json'
	
	@property
	def body_tester(self):
		return FriendsListBodyTester()
		
class CanvasTest(object):
	
	TYPE = ACCEPTS + 'canvas'
	IS_OBJ = True
	
	@property
	def setup_obj(self):
		return 'setup_canvas.json'
	
	@property
	def test_obj(self):
		return 'test_canvas.json'
	
	@property
	def response_value(self):
		return 'canvas_response.json'
	
	@property
	def body_tester(self):
		return CanvasBodyTester()
		
class CanvasShapeTest(object):
	
	TYPE = ACCEPTS + 'canvasshape'
	IS_OBJ = False
	
	@property
	def setup_obj(self):
		return 'setup_canvas_shape.json'
	
	@property
	def test_obj(self):
		return 'test_canvas_shape.json'
	
	@property
	def response_value(self):
		return 'canvas_shape_response.json'
	
	@property
	def body_tester(self):
		return CanvasShapeBodyTester()
		
class CanvasCircleShapeTest(object):
	
	TYPE = ACCEPTS + 'canvascircleshape'
	IS_OBJ = False
	
	@property
	def setup_obj(self):
		return 'setup_canvas_circle_shape.json'
	
	@property
	def test_obj(self):
		return 'test_canvas_circle_shape.json'
	
	@property
	def response_value(self):
		return 'canvas_circle_shape_response.json'
	
	@property
	def body_tester(self):
		return CanvasShapeBodyTester()
		
class CanvasPolygonShapeTest(object):
	
	TYPE = ACCEPTS + 'canvaspolygonshape'
	IS_OBJ = False
	
	@property
	def setup_obj(self):
		return 'setup_canvas_polygon_shape.json'
	
	@property
	def test_obj(self):
		return 'test_canvas_polygon_shape.json'
	
	@property
	def response_value(self):
		return 'canvas_polygon_shape_response.json'
	
	@property
	def body_tester(self):
		return CanvasPolygonShapeBodyTester()
	

