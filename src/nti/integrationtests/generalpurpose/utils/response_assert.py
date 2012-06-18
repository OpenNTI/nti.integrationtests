
import inspect

from hamcrest import assert_that, is_

class BodyTester(object):
	def testBody(self, parsedBody, mimeType, info):
		pass

class NoteBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.note'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['MimeType'], is_( mimeType ))
		assert_that( parsedBody['body'], is_( info ))

class HighlightBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.highlight'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['MimeType'], is_( mimeType ))
		assert_that( parsedBody['selectedText'], is_( info ))

class FriendsListBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.friendslist'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['MimeType'], is_( mimeType ))
		assert_that( parsedBody['realname'], is_( info ))

class CanvasBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.canvas'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['MimeType'], is_( mimeType ))
		assert_that( parsedBody["shapeList"][0]["strokeRGBAColor"], is_( info ))

class CanvasShapeBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.canvasshape'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['transform']['a'], is_( info['a'] ))
		assert_that( parsedBody['transform']['c'], is_( info['c'] ))
		assert_that( parsedBody['transform']['b'], is_( info['b'] ))
		assert_that( parsedBody['transform']['d'], is_( info['d'] ))
		assert_that( parsedBody['transform']['tx'], is_( info['tx'] ))
		assert_that( parsedBody['transform']['ty'], is_( info['ty']))

class CanvasCircleShapeBodyTester(CanvasShapeBodyTester):
	MIME_TYPE = 'application/vnd.nextthought.canvascircleshape'

class CanvasPolygonShapeBodyTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.canvaspolygonshape'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody["strokeRGBAColor"], is_( info ))

class QuizTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.quiz'

	def testBody(self, parsedBody, mimeType, info):
		assert_that( parsedBody['Items']['1']['Text'], is_( info[0]['1']['Text'] ))
		assert_that( parsedBody['Items']['1']['Answers'], is_( info[0]['1']['Answers'] ))

class QuizResultTester(BodyTester):

	MIME_TYPE = 'application/vnd.nextthought.quizresult'

	def testBody(self, parsedBody, mimeType, info):
        # JAM: TODO: These are probably backwards (actual vs expected)
		assert_that( info[0]['1']['Text'], is_( parsedBody['Items'][0]['Question']['Text'] ) )
		assert_that( info[0]['1']['Answers'], is_( parsedBody['Items'][0]['Question']['Answers'] ) )
		assert_that( info[0]['1']['Response'], is_( parsedBody['Items'][0]['Response'] ) )
		assert_that( info[0]['1']['Assessment'], is_( str(parsedBody['Items'][0]['Assessment']) ))



MIME_TYPE_REGISTRY = {}

for v in dict(locals()).itervalues():
	if inspect.isclass(v) and issubclass(v, BodyTester):
		if hasattr(v, 'MIME_TYPE'):
			MIME_TYPE_REGISTRY[v.MIME_TYPE] = v
            
