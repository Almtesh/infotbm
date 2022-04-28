from tbm_api_lib.stop import *
import sys
from datetime import datetime
from gmplot import gmplot

if __name__ == "__main__":
    for word in sys.argv[1:]:
        for area in search_stop_by_name(word):
            for stop in show_stops_from_ref(area["ref"])["stop_points"]:
                for route in stop["routes"]:
                    if "Tram" in route["line_human"]:
                        sr = StopRoute(stop["id"], route["line_id"])
                        line = sr.get_line()
                        for vehicule in line.vehicles():
                            v = line.get_vehicle(vehicule)
                            if v.is_realtime:
                                print(
                                    str(v.wait_time_text)
                                    + " ("
                                    + datetime.fromtimestamp(v.arrival).strftime(
                                        "%H:%M"
                                    )
                                    + ") → "
                                    + v.destination
                                    + " "
                                    + str(v.location)
                                )
                            else:
                                print(
                                    "~"
                                    + str(v.wait_time_text)
                                    + " ("
                                    + datetime.fromtimestamp(v.arrival).strftime(
                                        "%H:%M"
                                    )
                                    + ") → "
                                    + v.destination
                                    + " "
                                    + str(v.location)
                                )
                        # gmap = gmplot.GoogleMapPlotter(v.location[0], v.location[1], 13)
                        # gmap.marker(v.location[0], v.location[1], "cornflowerblue")
                        # gmap.draw("map.html")
