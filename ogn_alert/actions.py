class Action:
    def __init__(self, data_filter):
        self.data_filter = data_filter

    def __call__(self, data):
        self.action(self.data_filter(data))

    def action(self, filtered_data):
        pass


class PrintAction(Action):
    def __init__(self, data_filter):
        super().__init__(data_filter)

    def action(self, filtered_data):
        print(filtered_data)


class TriggerGPIOAction(Action):
    def __init__(self, data_filter, pin_id=17):
        super().__init__(data_filter)
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.pin_id = pin_id
        self.GPIO.setup(self.pin_id, self.GPIO.OUT)

    def action(self, filtered_data):
        if len(filtered_data.keys()):
            self.GPIO.output(self.pin_id, self.GPIO.HIGH)
        else:
            self.GPIO.output(self.pin_id, self.GPIO.LOW)
