from datetime import datetime
from urllib.request import urlopen

from ogn_alert.filters import Filter


class Action:
    '''
    Base class for implementing actions.
    Your custom action should inherit from this class and implement/override the action() method.
    '''
    def __init__(self, data_filter=Filter()):
        self.data_filter = data_filter

    def __call__(self, data):
        self.action(self.data_filter(data))

    def action(self, filtered_data):
        return None


class PrintAction(Action):
    def __init__(self, data_filter=Filter()):
        super().__init__(data_filter)

    def action(self, filtered_data):
        print("[", datetime.now(), "]", filtered_data)


class TriggerGPIOAction(Action):
    def __init__(self, pin_id=17, data_filter=Filter()):
        super().__init__(data_filter)
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.pin_id = pin_id
        self.GPIO.setup(self.pin_id, self.GPIO.OUT)

    def action(self, filtered_data):
        pin_state = self.GPIO.HIGH if len(filtered_data.keys()) else self.GPIO.LOW
        self.GPIO.output(self.pin_id, pin_state)


class HTTPRequestAction(Action):
    def __init__(self, url_on, url_off, response_action=None, data_filter=Filter()):
        super().__init__(data_filter)
        self.url = {
            "on": url_on,
            "off": url_off,
        }
        self.response_action = response_action
        self.current_state = "off"
        self.set_state(self.current_state)

    def set_state(self, state):
        if state == self.current_state:
            return
        with urlopen(self.url[state]) as response:
            self.current_state = state
            if self.response_action:
                self.response_action(response)

    def action(self, filtered_data):
        state = "on" if len(filtered_data.keys()) else "off"
        self.set_state(state)

