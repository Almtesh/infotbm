'''
Provides all info about V³ stations
'''

from libs import get_data_from_json
from time import time

vcub_url = 'https://ws.infotbm.com/ws/1.0/vcubs'


class Vcub ():
	'''
	Récupère les informations des stations V³
	
	Format de données, tel que retourné par le site infotbm :
	{
		lists: [
			{
				'id': numéro de la station,
				'name': str,
				'connexionState': 'CONNECTEE' si en service 'DECONNECTEE' sinon,
				'typeVlsPlus': 'VLS_PLUS' si V³+ 'PAS_VLS_PLUS' sinon,
				'nbPlaceAvailable': 33,
				'nbBikeAvailable': 0
				'nbElectricBikeAvailable': 6
				'latitude': float,
				'longitude': float,
			},
		]
	}
	'''
	def __init__ (self, autoupdate_at_creation = None, autoupdate = False, autoupdate_delay = -1, data = None):
		self.last_update = 0
		if type (data) == dict:
			self.data = self.update (data = data)
		else:
			self.data = None
		if autoupdate_at_creation or (autoupdate_at_creation is None and self.data is None):
			self.update ()
	
	def update (self, auto = False, data = None):
		'''
		Updates data
		auto optionnal param is to set if a update is a automatic one, and must be performed as defined in autoupdate_delay variable
		'''
		if data is None or type (data) != dict:
			d = get_data_from_json (vcub_url)
		else:
			d = data
		# the original format is awfull, so I change it a little
		if type (d) == dict:
			self.data = {}
			d = d ['lists']
			for i in d:
				e = {
					'name': i ['name'],
					'online': i ['connexionState'] == 'CONNECTEE',
					'plus': i ['typeVlsPlus'] == 'VLS_PLUS',
					'empty': int (i ['nbPlaceAvailable']),
					'bikes': int (i ['nbBikeAvailable']),
					'ebikes': int (i ['nbElectricBikeAvailable']),
					'location': (float (i ['latitude']), float (i ['longitude']))
				}
				self.data [int (i ['id'])] = e
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
				self.ebikes = self.data ['ebikes']
				self.empty = self.data ['empty']
			
			def __int__ (self):
				return (self.id)
		
		return (Station (self.data [id], id))
	
	def get_all_ids (self):
		return (tuple (self.data.keys ()))


if __name__ == '__main__':
	v = Vcub ()
	for i in (v.get_by_id (149), v.get_by_id (v.get_names () ['Buttiniere']), ):
		print ('%s (%d) (%f, %f)%s%s\n\tbikes: %d\n\te-bikes: %d\n\tfree: %d\n\t' % (i.name, i, i.location [0], i.location [1], i.isplus and ' (VCUB+)' or '', i.online and ' ' or ' OFFLINE', i.bikes, i.ebikes, i.empty))
	v = Vcub (data = get_data_from_json (vcub_url))
	for i in (v.get_by_id (v.get_locations () [(44.8875, -0.51763)]), ):
		print ('%s (%d) (%f, %f)%s%s\n\tbikes: %d\n\te-bikes: %d\n\tfree: %d\n\t' % (i.name, i, i.location [0], i.location [1], i.isplus and ' (VCUB+)' or '', i.online and ' ' or ' OFFLINE', i.bikes, i.ebikes, i.empty))
	print ('stations :', v.get_all_ids ())