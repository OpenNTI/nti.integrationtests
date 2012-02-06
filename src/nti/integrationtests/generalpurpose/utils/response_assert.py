
class NoteBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['body'] == info
		
class HighlightBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['startHighlightedText'] == info
		
class CanvasBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody["shapeList"][0]["strokeRGBAColor"] == info
	
class CanvasShapeBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['transform']['a'] == info['a']
		assert parsedBody['transform']['c'] == info['c']
		assert parsedBody['transform']['b'] == info['b']
		assert parsedBody['transform']['d'] == info['d']
		assert parsedBody['transform']['tx'] == info['tx']
		assert parsedBody['transform']['ty'] == info['ty']
		
class CanvasPolygonShapeBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody["strokeRGBAColor"] == info

class FriendsListBodyTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['MimeType'] == mimeType
		assert parsedBody['realname'] == info
		
class QuizTester(object):
	
	def testBody(self, parsedBody, mimeType, info):
		assert parsedBody['Items']['1']['Text'] == info[0]['1']['Text']
		assert parsedBody['Items']['1']['Answers'] == info[0]['1']['Answers']
	
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
		if lastModifiedTimeCollection:pass
#			assert lastModifiedTimeCollection <= preRequestTime
		if lastModifiedTime:
			assert lastModifiedTime <= preRequestTime