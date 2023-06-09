# Copy or rename this file to main.py and customize it to your needs

from ogn_alert import TriggerGPIOAction, GeofenceSection, GeofenceFilter, GlidernetBackendHandler, AprsHandler, TelnetHandler

'''
You can write normal python code, e.g. to define some useful filter functions.
A beacon has at least the following attributes which can be used for filtering:
 - latitude (in degrees)
 - longitude (in degrees)
 - altitude (in meters AMSL)
 - track (in degrees)
 - ground_speed (in km/h)
 - climb_rate (in m/s)
'''

def is_landing(beacon):
    return beacon["ground_speed"] > 20 and beacon["altitude"] < 750 and beacon["climb_rate"] < 0.5

def is_heading_towards(beacon, target_direction, tolerance_degrees=90):
    anglediff = (beacon["track"] - target_direction + 180 + 360) % 360 - 180 # avoid wrap-around at 360°
    return abs(anglediff) < tolerance_degrees


'''
Specify the geofence
'''
geofence = GeofenceFilter(
    includes=[  # give a list of GeofenceSections which should trigger alerts
        GeofenceSection(
            "polygon.kml",  # kml file that contains some closed polygons
            lambda beacon: is_landing(beacon) and is_heading_towards(beacon, 270)  # filter function
        )
    ],
    excludes=[]  # regions can also be excluded such that beacons therein do not trigger alerts
)


'''
Select the alert action and pass the geofence
'''
action = TriggerGPIOAction(geofence, pin_id=17)


'''
Finally, select your data handler, i.e. the source of your OGN data stream
'''

# This connects directly to the APRS servers, use a filter to reduce the amount of received data, e.g. "r/lat/lon/distance"
data_handler = AprsHandler(action, aprs_filter='r/50/12/200')

# This uses the glidernet backend (https://github.com/glidernet/ogn-live#backend)
# data_handler = GlidernetBackendHandler(action, lat_bounds=[49, 51], lon_bounds=[11, 13])

# This connects to the local telnet stream of an OGN receiver
# data_handler = TelnetHandler(action)


'''
Start the analysis of OGN data
'''
data_handler.run()
