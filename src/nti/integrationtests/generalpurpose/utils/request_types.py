#'''
#Created on Jan 18, 2012
#
#@author: ltesti
#'''
#
#class Successful(object):
#	
#	@property
#	def input_info(self):
#		return {}
#	
#	@property
#	def if_modified_since_no(self):
#		return 304
#	
#	@property 
#	def if_modified_since_yes(self):
#		return 200
#	
#	@property
#	def get(self):
#		return 200
#	
#	@property
#	def post(self):
#		return 201
#	
#	@property
#	def put(self):
#		return 200
#	
#	@property
#	def delete(self):
#		return 204
#	
#class Unauthorized(object):
#	
#	@property
#	def input_info(self):
#		return {"password":"incorrect"}
#	
#	@property
#	def if_modified_since_no(self):
#		return 401
#	
#	@property 
#	def if_modified_since_yes(self):
#		return 401
#	
#	@property
#	def get(self):
#		return 401
#	
#	@property
#	def post(self):
#		return 401
#	
#	@property
#	def put(self):
#		return 401
#	
#	@property
#	def delete(self):
#		return 401
#	
#class NotFound(object):
#	
#	@property
#	def input_info(self):
#		return {"id":"/dataserver2/users/logan.testi%40nextthought.com/Objects/tag%3Anextthought.com%2C2011-10%3Alogan.testi%40nextthought.com-OID-0x03", 
#				"href":"/dataserver2/users/logan.testi%40nextthought.com/doesNotExist"}
#	
#	@property
#	def if_modified_since_no(self):
#		return 404
#	
#	@property 
#	def if_modified_since_yes(self):
#		return 404
#	
#	@property
#	def get(self):
#		return 404
#	
#	@property
#	def post(self):
#		return 404
#	
#	@property
#	def put(self):
#		return 404
#	
#	@property
#	def delete(self):
#		return 404
#	
#class BadData(object):
#	
#	@property
#	def input_info(self):
#		return {"objData":"badData"}
#	
#	@property
#	def if_modified_since_no(self): pass
#	
#	@property 
#	def if_modified_since_yes(self): pass
#	
#	@property
#	def get(self): pass
#	
#	@property
#	def post(self):
#		return 500
#	
#	@property
#	def put(self):
#		return 500
#	
#	@property
#	def delete(self): pass
#	