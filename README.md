# ogn-alert

This python module can be used to trigger alerts and actions based on geofenced and filtered data of the [Open Glider Network](https://www.glidernet.org/) (OGN).
Actions for sending HTTP requests and for triggering a GPIO pin on a Raspberry Pi are provided.
Custom actions can easily be added, see `ogn_alert/actions.py` for implementation details.
OGN data is obtained either from the web (via the APRS servers or the [API](https://github.com/glidernet/ogn-live#backend) of [https://live.glidernet.org](https://live.glidernet.org)) or directly from the data stream of a local OGN receiver.

## Install

You need the following libraries, which can be installed individually with `pip install <library>`.
Install all with `pip install -r requirements.txt`.
- `ogn-client`
- `shapely`
- `RPi.GPIO` (optional, if using `TriggerGPIOAction`)

You can install the module itself with `pip install -e .` system-wide, although this is not required if the run script is located in this directory.

## Configure

Write your own `main.py` script to configure and run ogn-alert.
Refer to the provided template for further instructions.

Note that there are multiple options to subscribe to OGN data.
If you run this module directly on an OGN receiver, `TelnetHandler` can be used to analyze the OGN data stream locally.
To use OGN data from the web, select either `AprsHandler` with a suitable `aprs_filter` (e.g. `"r/<lat>/<lon>/<distance>"`) or `GlidernetBackendHandler` with some latitude and longitude bounds.

## Automate

To automatically start ogn-alert on boot, set up a systemd service using the template `ogn-alert.service`.
Edit this file and make sure that `ExecStart` points to your `main.py` script.
You might also want to change other options, e.g. when and how the script is restarted if a failure occurs.
Then, enable and start the service as follows:

```shell
$ sudo cp ogn-alert.service /etc/systemd/system/
$ sudo systemctl enable --now ogn-alert
```

Check if ogn-alert is running:
```shell
$ systemctl status ogn-alert
```

If you change `main.py`, the service has to be restarted with `sudo systemctl restart ogn-alert`.
