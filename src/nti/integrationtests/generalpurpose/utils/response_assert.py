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
	
# -----------------------------------

class LastModifiedAssessment(object):
	
	@classmethod	
	def changedLastModifiedTime(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		lastModifiedTime = kwargs.get('requestTime', None)
		preRequestTime = kwargs['preRequestTime']
		if lastModifiedTimeCollection:
			assert lastModifiedTimeCollection >= preRequestTime
		if lastModifiedTime:
			assert lastModifiedTime >= preRequestTime
	
	@classmethod	
	def unchangedLastModifiedTime(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		lastModifiedTime = kwargs.get('requestTime', None)
		preRequestTime = kwargs['preRequestTime']
		
		#TODO: What do we need to do here?
		if lastModifiedTimeCollection:
			pass

		if lastModifiedTime:
			assert lastModifiedTime <= preRequestTime
			
# -----------------------------------

MIME_TYPE_REGISTRY = {}

for v in dict(locals()).itervalues():
	if inspect.isclass(v) and issubclass(v, BodyTester):		
		if hasattr(v, 'MIME_TYPE'):
			MIME_TYPE_REGISTRY[v.MIME_TYPE] = v
		
			