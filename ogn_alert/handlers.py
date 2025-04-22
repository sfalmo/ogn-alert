import requests
from time import sleep
from threading import Timer, Lock
from datetime import date, time, datetime, timezone
from xml.etree import ElementTree
from ogn.client import TelnetClient, AprsClient
from ogn.parser.telnet_parser import parse as parse_telnet
from ogn.parser import parse as parse_aprs
from ogn.parser import ParseError


class Handler:
    def __init__(self, actions, max_age_seconds=30):
        self.data = {}
        try:
            iter(actions)
            self.actions = actions
        except TypeError:
            self.actions = [actions]
        self.max_age_seconds = max_age_seconds
        self.lock = Lock()

    def trigger_actions(self):
        for action in self.actions:
            action(self.data)

    def remove(self, address):
        with self.lock:
            if address not in self.data:
                return
            del self.data[address]
            self.trigger_actions()

    def update(self, beacon):
        with self.lock:
            if not beacon or "address" not in beacon or "timestamp" not in beacon:
                return
            address = beacon["address"]
            if address in self.data and "timer" in self.data[address]:
                self.data[address]["timer"].cancel()
            self.data[address] = beacon
            self.data[address]["timer"] = Timer(self.max_age_seconds, self.remove, [address])
            self.data[address]["timer"].name = "Thread-" + address
            self.data[address]["timer"].start()
            self.trigger_actions()

    def run(self):
        pass


class MockHandler(Handler):
    def __init__(self, action, beacons, repeat_interval=10, **kwargs):
        super().__init__(action, **kwargs)
        self.beacons = beacons
        self.repeat_interval = repeat_interval

    def run(self):
        while True:
            for beacon in self.beacons:
                beacon["timestamp"] = datetime.now(timezone.utc)
                self.update(beacon)
            sleep(self.repeat_interval)


class TelnetHandler(Handler):
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


class AprsHandler(Handler):
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


class GlidernetBackendHandler(Handler):
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
