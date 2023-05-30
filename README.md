# ogn-alert

This python module can be used to trigger alerts based on geofenced and filtered data of the [Open Glider Network](https://www.glidernet.org/) (OGN).
Currently, an alert for controlling the state of a GPIO pin on a Raspberry Pi is implemented, although other alerts can easily be added.
The module has multiple data handlers such that it can be used stand-alone or within an OGN receiver station.

## Install

You need the following libraries, which can be installed with `pip install`:
- `ogn-client`
- `shapely`
- `RPi` (optional, if using `TriggerGPIOAction`)

## Configure

Write your own `main.py` script to configure ogn-alert.
For this, the provided template might be helpful and contains further comments.

There are multiple options to subscribe to OGN data.
If you run this module directly on an OGN receiver, `TelnetHandler` can be used to analyze the local data stream directly (no data is fetched from the internet).
To get OGN data from the web, use either `AprsHandler` with a suitable `aprs_filter` (e.g. `"r/<lat>/<lon>/<distance>"`) or `GlidernetBackendHandler` with some latitude and longitude bounds.

## Automate

To automatically start ogn-alert on boot, set up a systemd service as follows (you might have to change the file path in `ogn-alert.service` first):

```shell
$ sudo cp ogn-alert.service /etc/systemd/system/
$ sudo systemctl enable --now ogn-alert
```

To pick up changes in `main.py`, the daemon has to be restarted with `sudo systemctl restart ogn-alert`.
