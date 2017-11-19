'''
Provides all info about V³ stations
'''

from libs import get_data_from_json
from time import time

vcub_url = 'http://plandynamique.infotbm.com/api/vcub'

class Vcub ():
	'''
	Gather V³ stations informations
	
	data format as returned by infotbm:
	{
		FeatureCollection: {
			gml:featureMember: [
				{
					bm:CI_VCUB_P: {
						bm:ETAT: str, # CONNECTEE if on, DECONNECTEE either
						bm:TYPE: str, # VLS+ for V³+ and VLS for regular V³ station
						gml:boundedBy: dict,
						gml:id: str,
						bm:NBPLACES: int, # empty spaces
						bm:GID: int,
						bm:NBVELOS: int, # available bikes
						bm:HEURE: str,
						bm:IDENT: int, # id as written on the station
						bm:geometry: dict,
						bm:NOM: str, # HR name
					},
				},
			],
			... # the rest is quite useless internal data
		},
	}
	'''
	def __init__ (self, autoupdate_at_creation = True, autoupdate = False, autoupdate_delay = -1):
		self.last_update = 0
		self.data = None
		if autoupdate_at_creation:
			self.update ()
	
	def update (self, auto = False):
		'''
		Updates data
		auto optionnal param is to set if a update is a automatic one, and must be performed as defined in autoupdate_delay variable
		'''
		d = get_data_from_json (vcub_url)
		# the original format is awfull, so I change it a little
		if d != False:
			self.data = {}
			d = d ['FeatureCollection']['gml:featureMember']
			for i in d:
				j = i ['bm:CI_VCUB_P']
				l = j ['bm:geometry'] ['gml:Point'] ['gml:pos'].split (' ')
				e = {
					'name': j ['bm:NOM'],
					'online': j ['bm:ETAT'] == 'CONNECTEE',
					'plus': j['bm:TYPE'] == 'VLS+',
					'empty': int (j ['bm:NBPLACES']),
					'bikes': int (j ['bm:NBVELOS']),
					'location': (float (l [0]), float (l [1]))
					}
				self.data [int (j ['bm:IDENT'])] = e
			self.last_update = time ()
	
	def data_age (self):
		'''
		Computes the data's age
		'''
		return (time () - self.last_update)
	
	def get_names (self):
		'''
		Returns all names in a dict with id as data
		'''
		r = {}
		for i in self.data:
			r [self.data [i] ['name']] = i
		return (r)
	
	def get_locations (self):
		'''
		Returns all locations in a dict with id as data
		'''
		r = {}
		for i in self.data:
			r [self.data [i] ['location']] = i
		return (r)
	
	def get_by_id (self, id):
		'''
		Returns a station by its id
		'''
		class Station ():
			'''
			A V³ station
			'''
			def __init__ (self, data, id):
				self.data = data
				self.id = id
				self.name = self.data ['name']
				self.location = self.data ['location']
				self.online = self.data ['online']
				self.isplus = self.data ['plus']
				self.bikes = self.data ['bikes']
				self.empty = self.data ['empty']
			
			def __int__ (self):
				return (self.id)
		
		return (Station (self.data [id], id))

if __name__ == '__main__':
	v = Vcub ()
	for i in (v.get_by_id (149), v.get_by_id (v.get_names ()['Buttiniere']), v.get_by_id (v.get_locations () [(44.8875, -0.51763)])):
		print ('%s (%d) (%f, %f)%s%s\n\tbikes: %d\n\tfree: %d\n\t' % (i.name, i, i.location [0], i.location [1], i.isplus and ' (VCUB+)' or '', i.online and ' ' or ' OFFLINE', i.bikes, i.empty))