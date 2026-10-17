# External sensor inputs

The dashboard accepts oil pressure, transmission/oil temperature and outside temperature from a timestamped JSON file. This is the integration point for a separately installed, calibrated sensor controller or a verified vehicle-specific decoder.

## File format

```json
{
  "timestamp": 1792270000.0,
  "values": {
    "oil_pressure": 44.0,
    "trans_temp": 82.0,
    "oil_temp": 100.0,
    "ambient_temp": 23.0
  }
}
```

These numbers are format examples, not calibration targets or normal operating specifications. `timestamp` must be the current Unix time in seconds, updated with every sample. Oil pressure is **psi**; temperatures are **degrees Celsius**, regardless of the screen's display units. Include only sensors actually measured. Null values are treated as unavailable.

Run:

```sh
python OBDII.py --port COM7 --sensors sensors.json
```

Samples older than five seconds, timestamps over two seconds in the future, malformed files, nonnumeric values and out-of-range readings are rejected. Missing/invalid feeds never become zero pressure. Oil temperature and outside temperature use the external feed only when a current OBD reading is unavailable. Oil pressure/transmission temperature always use the external feed in live mode.

## Serial controller bridge

The included bridge reads newline-delimited JSON from a **separate sensor controller's** serial port. It does not use the OBD adapter's port. The controller must emit already calibrated physical values, for example:

```json
{"oil_pressure": 44.0, "trans_temp": 82.0}
```

Run it in another terminal:

```sh
python tools/sensor_bridge.py --port COM8 --baudrate 115200 --output sensors.json
```

It validates numbers, adds a current timestamp and replaces the output file atomically. If serial input stops, the dashboard expires the previous sample. Invalid input is skipped; no synthetic fallback is written. Restart the bridge after disconnecting/reconnecting its controller.

No wiring, sender calibration or Chrysler-enhanced PID definition is assumed by the software. Hardware-specific conversion belongs in the controller/verified decoder. Do not connect an unknown electrical signal directly to a computer or alter the factory sender circuit based on this file format.
