'''
Provides all info from a stop
'''

from libs import get_data_from_json
from time import time

stop_schedule_url = 'http://plandynamique.infotbm.com/api/schedules?stop=%d'

def get_stop_list ():
	'''
	Gets stop name after its number
	'''
	l = {}
	
	# Trams
	data = get_data_from_json ('http://plandynamique.infotbm.com/api/file/trams.xml')
	for i in data ['arret']:
		n = []
		if type (i ['ligne']) == dict:
			n.append (int (i ['ligne'] ['StopPointExternalCode'].replace ('TBT', '')))
		else:
			for j in i ['ligne']:
				n.append (int (j ['StopPointExternalCode'].replace ('TBT', '')))
		for j in n:
			l [j] = i ['nom']
	#Bus
	data = get_data_from_json ('http://plandynamique.infotbm.com/api/file/bus.xml')
	for i in data ['arret']:
		n = int (i ['StopPointExternalCode'].replace ('TBC', ''))
		l [n] = i ['StopName']
	
	return (l)

class Stop ():
	'''
	Gather stop informations
	
	data format as returned by infotbm:
	[
		{
			origin: str, # source de l'information, BDSI tout le temps semble-t-il
			type: str, # type de ligne (Bus, Tramway, Ferry)
			message: str,
			code: str, # nom de la ligne
			name: str, # nom complet de la ligne
			schedules: [
				{
					arrival: str,
					arrival_commande: str,
					arrival_theorique: str,
					comment: str,
					departure: str,
					departure_commande: str,
					departure_theorique: str,
					destination_id: int,
					destination_name: str,
					origin: str,
					realtime: int,
					schedule_id: int,
					trip_id: int,
					updated_at: str, # last data update
					vehicle_id: int,
					vehicle_lattitude: float,
					vehicle_longitude: float,
					vehicle_position_updated_at: str, # last update from vehicle
					waittime: str, # estimated wait time in %H:%M:%S format
					waittime_text: str # human readable estimated wait time written in French
				},
			],
		}
	]
	'''
	
	def __init__ (self, number, autoupdate_at_creation = True, autoupdate = False, autoupdate_delay = -1):
		self.number = number
		self.last_update = 0
		self.data = None
		if autoupdate_at_creation:
			self.update ()
	
	def update (self, auto = False):
		'''
		Updates data
		auto optionnal param is to set if a update is a automatic one, and must be performed as defined in autoupdate_delay variable
		'''
		self.data = get_data_from_json (stop_schedule_url % self.number)
		if self.data == False:
			self.data = None
			self.last_update = 0
		else:
			self.last_update = time ()
	
	def data_age (self):
		'''
		Computes the data's age
		'''
		return (time () - self.last_update)
	
	def lines (self):
		'''
		List lines on the stop
		Return unique indexes as known by the class
		'''
		return (list (range (0, len (self.data))))
	
	def get_line (self, line):
		class Line ():
			'''
			Information about a line on a stop
			'''
			def __init__ (self, data):
				self.data = data
			
			def number (self):
				return (self.data ['code'])
			
			def name (self):
				return (self.data ['name'])
			
			def vehicles_type (self):
				return (self.data ['type'])
			
			def vehicles (self):
				return (list (range (0, len (self.data ['schedules']))))
			
			def get_vehicle (self, vehicle):
				class Vehicle ():
					'''
					Information about a vehicle
					'''
					def __init__ (self, data):
						self.data = data
					
					def is_realtime (self):
						return (self.data ['realtime'] == '1')
					
					def waittime (self):
						return (self.data ['waittime'])
					
					def waittime_hr (self):
						return (self.data ['waittime_text'])
					
					def destination (self):
						return (self.data ['destination_name'])
					
					def number (self):
						return (str (self.data ['vehicle_id']))
					
					def location (self):
						try:
							return (float (self.data ['vehicle_lattitude']), float (self.data ['vehicle_longitude']))
						except:
							return (None)
				
				return (Vehicle (self.data ['schedules'] [vehicle]))
		
		return (Line (self.data [line]))
	

if __name__ == '__main__':
	stop_names = get_stop_list ()
	for i in (3687, 1922, 5832):
		print (str (i) + ' (' + stop_names [i] + ')')
		s = Stop (i)
		for j in s.lines ():
			l = s.get_line (j)
			print ('\t' + l.vehicles_type () + ' ' + l.number () + ' (' + l.name () + ')')
			for k in l.vehicles ():
				v = l.get_vehicle (k)
				if v.is_realtime ():
					print ('\t\t' + v.waittime_hr () + ' → ' + v.destination ())
				else:
					print ('\t\t~' + v.waittime_hr () + ' → ' + v.destination ())