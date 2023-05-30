import time

from actions import PrintAction
from data_filters import Geometry, GeofenceFilter
from data_handlers import TelnetHandler, AprsHandler, GlidernetBackendHandler

data_filter = GeofenceFilter(
    includes=[
        Geometry(
            ((49, 12), (50, 12), (50, 13), (49, 13), (49, 12)),
            [lambda beacon: beacon["ground_speed"] > 20 and beacon["climb_rate"] < 0.5 and beacon["altitude"] < 1000]
        )
    ],
    excludes=[]
)

action = PrintAction(data_filter)

# data_handler = AprsHandler(action, aprs_filter='r/50/12/50')

# data_handler = TelnetHandler(action)

data_handler = GlidernetBackendHandler(action, lat_bounds=[49, 51], lon_bounds=[11, 13])

data_handler.run()

