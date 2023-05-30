# Copy or rename this file to main.py and customize it to your needs

from actions import TriggerGPIOAction
from filters import GeofenceSection, GeofenceFilter
from data_handlers import GlidernetBackendHandler, AprsHandler, TelnetHandler


# A beacon has at least the following attributes which can be used for filtering:
# latitude, longitude, altitude, track, ground_speed, climb_rate

# You can write normal python code, e.g. to define some useful filter functions

def is_landing(beacon):
    return beacon["ground_speed"] > 20 and beacon["altitude"] < 750 and beacon["climb_rate"] < 0.5

def is_heading(beacon, target_direction, tolerance_degrees=90):
    anglediff = (beacon["track"] - target_direction + 180 + 360) % 360 - 180 # avoid wrap-around at 360°
    return abs(anglediff) < tolerance_degrees


# Specify the geofence
filt = GeofenceFilter(
    includes=[  # give a list of GeofenceSections which should trigger alerts
        GeofenceSection(
            ((49, 12), (50, 12), (50, 13), (49, 13), (49, 12)),  # vertices (lat, lon) of a closed polygon
            lambda beacon: is_landing(beacon) and is_heading(beacon, 270)  # filter function
        )
    ],
    excludes=[]  # you can also exclude regions explicitly, in which no action shall be triggered
)


# Select the alert action and pass the geofence
action = TriggerGPIOAction(filt)


# Finally, select your data handler, i.e. the source of your OGN data stream
data_handler = AprsHandler(action, aprs_filter='r/50/12/200')
# data_handler = GlidernetBackendHandler(action, lat_bounds=[49, 51], lon_bounds=[11, 13])
# data_handler = TelnetHandler(action)


# Start the analysis of OGN data
data_handler.run()
