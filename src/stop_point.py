class StopPoint:
	def __init__ (self, name):
		self.id = None
		self.name = name
		self.routes = []

	def getId (self):
		return self.id

	def getName (self):
		return self.name

	def getRoutes (self):
		return self.routes

	def setId (self, id):
		self.id = id

	def setRoutes (self, routes):
		self.routes = routes

	def __repr__ (self):
		return self.name

	def __str__ (self):
		return self.name