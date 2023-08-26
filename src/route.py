class Route:
	def __init__ (self, line_id, name, line_name):
		self.id = None
		self.name = name
		self.line_name = line_name
		self.line_id = line_id

	def getId (self):
		return self.id

	def getName (self):
		return self.name

	def getLineName (self):
		return self.line_name
	
	def getLineId (self):
		return self.line_id

	def setId (self, id):
		self.id = id

	def __repr__ (self):
		return self.name + ' (' + self.line_name + ')'

	def __str__ (self):
		return self.name + ' (' + self.line_name + ')'