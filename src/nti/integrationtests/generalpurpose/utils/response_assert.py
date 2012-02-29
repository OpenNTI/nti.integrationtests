import inspect

class BodyTester(object):
	def testBody(self, parsedBody, mimeType, info):
		pass

class NoteBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.note'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['body'] == info
		
class HighlightBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.highlight'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['startHighlightedText'] == info
		
class FriendsListBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.friendslist'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['realname'] == info
		
class CanvasBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.canvas'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody["shapeList"][0]["strokeRGBAColor"] == info
	
class CanvasShapeBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.canvasshape'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['transform']['a'] == info['a']
		assert parsedBody['transform']['c'] == info['c']
		assert parsedBody['transform']['b'] == info['b']
		assert parsedBody['transform']['d'] == info['d']
		assert parsedBody['transform']['tx'] == info['tx']
		assert parsedBody['transform']['ty'] == info['ty']
		
class CanvasCircleShapeBodyTester(CanvasShapeBodyTester):
	MIME_TYPE = 'application/vnd.nextthought.canvascircleshape'

class CanvasPolygonShapeBodyTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.canvaspolygonshape'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody["strokeRGBAColor"] == info
		
class QuizTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.quiz'
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['Items']['1']['Text'] == info[0]['1']['Text']
		assert parsedBody['Items']['1']['Answers'] == info[0]['1']['Answers']
		
class QuizResultTester(BodyTester):
	
	MIME_TYPE = 'application/vnd.nextthought.quizresult'
	
	def testBody(self, parsedBody, mimeType, info):
		assert info[0]['1']['Text'] == parsedBody['Items'][0]['Question']['Text']
		assert info[0]['1']['Answers'] == parsedBody['Items'][0]['Question']['Answers']
		assert info[0]['1']['Response'] == parsedBody['Items'][0]['Response']
		assert info[0]['1']['Assessment'] == str(parsedBody['Items'][0]['Assessment'])
	
# -----------------------------------

MIME_TYPE_REGISTRY = {}

for v in dict(locals()).itervalues():
	if inspect.isclass(v) and issubclass(v, BodyTester):		
		if hasattr(v, 'MIME_TYPE'):
			MIME_TYPE_REGISTRY[v.MIME_TYPE] = v
		
			