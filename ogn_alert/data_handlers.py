import requests
from time import sleep
from threading import Timer
from datetime import date, time, datetime, timedelta
from xml.etree import ElementTree
from ogn.client import TelnetClient, AprsClient
from ogn.parser.telnet_parser import parse as parse_telnet
from ogn.parser import parse as parse_aprs
from ogn.parser import ParseError


class DataHandler:
    def __init__(self, actions, action_interval_seconds=0, max_age_seconds=30):
        self.data = {}
        try:
            iter(actions)
            self.actions = actions
        except TypeError:
            self.actions = [actions]
        self.action_interval_seconds = action_interval_seconds
        self.max_age_seconds = max_age_seconds
        self.last_action_time = datetime.utcnow()

    def purge_old_records(self):
        for address in list(self.data.keys()):
            if datetime.utcnow() - self.data[address]["timestamp"] > timedelta(seconds=self.max_age_seconds):
                del self.data[address]

    def update(self, beacon=None):
        if beacon:
            self.data[beacon["address"]] = beacon
            Timer(self.max_age_seconds, self.update).start()
        if datetime.utcnow() - self.last_action_time > timedelta(seconds=self.action_interval_seconds):
            self.purge_old_records()
            for action in self.actions:
                action(self.data)
            self.last_action_time = datetime.utcnow()

    def run(self):
        pass


class TelnetHandler(DataHandler):
    def __init__(self, action, **kwargs):
        super().__init__(action, **kwargs)
        self.client = TelnetClient()
        self.client.connect()

    def run(self):
        self.client.run(callback=self.process_beacon)

    def process_beacon(self, raw_message):
        beacon = parse_telnet(raw_message)
        if beacon:
            self.update(beacon)


class AprsHandler(DataHandler):
    def __init__(self, action, aprs_filter, **kwargs):
        super().__init__(action, **kwargs)
        self.client = AprsClient(aprs_user='N0CALL', aprs_filter=aprs_filter)
        self.client.connect()

    def run(self):
        self.client.run(callback=self.process_beacon, autoreconnect=True)

    def process_beacon(self, raw_message):
        try:
            beacon = parse_aprs(raw_message)
            if "address" in beacon and "aprs_type" in beacon and "receiver_name" in beacon and beacon["aprs_type"] == "position":
                self.update(beacon)
        except (ParseError, NotImplementedError):
            pass


class GlidernetBackendHandler(DataHandler):
    def __init__(self, action, lat_bounds, lon_bounds, request_interval_seconds=5, **kwargs):
        super().__init__(action, **kwargs)
        self.url = f"http://live.glidernet.org/lxml.php?a=0&b={lat_bounds[1]}&c={lat_bounds[0]}&d={lon_bounds[1]}&e={lon_bounds[0]}"
        self.request_interval_seconds = request_interval_seconds
        self.key_schema = ["latitude", "longitude", "callsign_short", "callsign", "altitude", "timestamp", "age", "track", "ground_speed", "climb_rate", "?", "receiver", "flarm_id", "address"]

    def run(self):
        while True:
            response = requests.get(self.url)
            markers = ElementTree.fromstring(response.content)
            for marker in markers:
                self.process_beacon(marker.attrib["a"])
            sleep(self.request_interval_seconds)

    def process_beacon(self, raw_message):
        beacon = {}
        for key, value in zip(self.key_schema, raw_message.split(",")):
            beacon[key] = value
        beacon["timestamp"] = datetime.combine(date.today(), time.fromisoformat(beacon["timestamp"]))
        for key in ["latitude", "longitude", "altitude", "age", "track", "ground_speed", "climb_rate"]:
            beacon[key] = float(beacon[key])
        self.update(beacon)
