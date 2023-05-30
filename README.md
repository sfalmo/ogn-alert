# ogn-alert

This python module can be used to trigger alerts based on geofenced and filtered data of the [Open Glider Network](https://www.glidernet.org/) (OGN).
An alert for triggering a GPIO pin on a Raspberry Pi is provided and other custom alerts can easily be added.
You can choose from multiple data handlers such that the module works stand-alone over the web or directly with the local data of an OGN receiver.

## Install

You need the following libraries, which can be installed individually with `pip install <library>`.
Install all with `pip install -r requirements.txt`.
- `ogn-client`
- `shapely`
- `RPi.GPIO` (optional, if using `TriggerGPIOAction`)

You can install the module itself with `pip install -e .` system-wide, although this is not required if the run script is located in this directory.

## Configure

Write your own `main.py` script to configure ogn-alert.
Refer to the provided template for further instructions.

Note that there are multiple options to subscribe to OGN data.
If you run this module directly on an OGN receiver, `TelnetHandler` can be used to analyze the local OGN data stream.
To use OGN data from the web, select either `AprsHandler` with a suitable `aprs_filter` (e.g. `"r/<lat>/<lon>/<distance>"`) or `GlidernetBackendHandler` with some latitude and longitude bounds.

## Automate

To automatically start ogn-alert on boot, set up a systemd service as follows (you might have to change the file path in `ogn-alert.service` first):

```shell
$ sudo cp ogn-alert.service /etc/systemd/system/
$ sudo systemctl enable --now ogn-alert
```

To pick up changes in `main.py`, the daemon has to be restarted with `sudo systemctl restart ogn-alert`.
