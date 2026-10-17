import argparse
import json
import math
import os
from pathlib import Path
import tempfile
import time


RANGES = {'oil_pressure': (0, 200), 'trans_temp': (-40, 215),
          'oil_temp': (-40, 215), 'ambient_temp': (-40, 100)}


def publish(line, destination):
    values = json.loads(line)
    if not isinstance(values, dict) or not values or set(values) - RANGES.keys():
        raise ValueError('Expected a JSON object containing supported sensor keys')
    for key, value in values.items():
        lower, upper = RANGES[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Sensor values must be finite numbers')
        if not lower <= value <= upper:
            raise ValueError('Sensor value outside supported range')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=destination.parent, delete=False, encoding='utf-8') as output:
            temp_path = Path(output.name)
            json.dump({'timestamp': time.time(), 'values': values}, output, allow_nan=False)
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Publish calibrated serial sensor readings for the dashboard')
    parser.add_argument('--port', required=True)
    parser.add_argument('--baudrate', type=int, default=115200)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import serial
    try:
        with serial.Serial(args.port, args.baudrate, timeout=1) as device:
            while True:
                line = device.read_until(b'\n', 4096)
                if not line:
                    continue
                try:
                    if not line.endswith(b'\n'):
                        device.reset_input_buffer()
                        raise ValueError('Incomplete sensor line')
                    publish(line, args.output)
                except (ValueError, UnicodeDecodeError) as error:
                    print(f'Skipped sensor reading: {error}')
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
