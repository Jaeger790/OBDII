# OBD-II Dashboard

Python desktop prototype for displaying vehicle data with PyQt5 and python-OBD.

## Setup

```sh
python -m venv .venv
python -m pip install -r requirements.txt
python OBDII.py
```

Activate the virtual environment before installing. A compatible OBD-II adapter and driver are required. Set `OBD_PORT` to your serial port, such as `COM7` on Windows or `/dev/ttyUSB0` on Linux. If unset, python-OBD uses automatic port detection.

## Layout

- `OBDII.py`: application entry point.
- `Engine_Commands.py`: adapter connection and queries.
- `UI/`: gauge and diagnostic widgets.
- `RPM_Gauge.py`: separate earlier gauge experiment.

## Status

Hardware-dependent prototype. This cleanup removes the nested Qt application/event loop from the main gauge window and makes the serial port configurable. Gauges still need testing with real adapter responses and disconnected hardware. No vehicle validation was performed during this review.
## Related projects

See the [project index](https://github.com/Jaeger790#projects) for the rest of my work.
