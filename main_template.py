# Copy or rename this file to main.py and customize it to your needs

import os
from ogn_alert import TriggerGPIOAction, HTTPRequestAction, GeofenceSection, GeofenceFilter, GlidernetBackendHandler, AprsHandler, TelnetHandler

'''
It is useful to first define functions for filtering beacons.
A beacon has at least the following attributes which can be used for filtering:
 - latitude (in degrees)
 - longitude (in degrees)
 - altitude (in meters AMSL)
 - track (in degrees)
 - ground_speed (in km/h)
 - climb_rate (in m/s)
'''

def is_landing(beacon):
    return beacon["ground_speed"] > 20 and beacon["altitude"] < 750 and beacon["climb_rate"] < 1.5

def is_heading_towards(beacon, target_direction, tolerance_degrees=90):
    anglediff = (beacon["track"] - target_direction + 180 + 360) % 360 - 180 # avoid wrap-around at 360°
    return abs(anglediff) < tolerance_degrees


'''
Specify the geofence
'''
geofence_filter = GeofenceFilter(
    includes=[  # give a list of GeofenceSections which should trigger alerts
        GeofenceSection(
            os.path.dirname(os.path.abspath(__file__)) + "/polygon.kml",  # kml file that contains some closed polygons (use absolute path so that the script can be called from anywhere, e.g. also from a systemd service)
            lambda beacon: is_landing(beacon) and is_heading_towards(beacon, 270)  # filter function
        )
    ],
    excludes=[]  # regions can also be excluded such that beacons therein do not trigger alerts
)


'''
Select the actions to be triggered
'''
actions = [
    HTTPRequestAction(url_on="http://localhost:8000/on", url_off="http://localhost:8000/off", data_filter=geofence_filter),
    TriggerGPIOAction(pin_id=17, data_filter=geofence_filter),
]


'''
Finally, select your data handler, i.e. the source of your OGN data stream
'''

# This connects directly to the APRS servers, use a filter to reduce the amount of received data, e.g. "r/lat/lon/distance"
handler = AprsHandler(actions, aprs_filter='r/50/12/100')

# This uses the glidernet backend (https://github.com/glidernet/ogn-live#backend)
# handler = GlidernetBackendHandler(actions, lat_bounds=[49, 51], lon_bounds=[11, 13])

# This connects to the local telnet stream of an OGN receiver
# handler = TelnetHandler(actions)


'''
Start the analysis of OGN data
'''
handler.run()
