import sys
from stop_area import *
from stop import *
from stop_route import StopRoute
from datetime import datetime


if __name__ == '__main__':
	for word in sys.argv [1:]:
		for area in get_stop_areas_by_name (word):
			stop = get_stop_by_id (area.getId ())
			for stopPoint in stop.getStopPoints ():
				for route in stopPoint.getRoutes ():
					if 'Tram' in route.getLineName ():
						stopRoute = StopRoute (stopPoint.getId (), route.getId (), route.getLineId ())
						line = stopRoute.get_line ()
						for vehicule in line.get_vehicles ():
							v = line.get_vehicle (vehicule)
							if v.getRealtime ():
								print (
									str (v.getWaitTimeText ())
									+ ' ('
									+ datetime.fromtimestamp (v.getArrival ()).strftime (
										'%H:%M'
									)
									+ ') → '
									+ v.getDestination ()
									+ ', Curr location: '
									+ str (v.getLocation ())
								)
							else:
								print (
									'~'
									+ str (v.getWaitTimeText ())
									+ ' ('
									+ datetime.fromtimestamp (v.getArrival ()).strftime (
										'%H:%M'
									)
									+ ') → '
									+ v.getDestination ()
									+ ', Curr location: '
									+ str (v.getLocation ())
								)