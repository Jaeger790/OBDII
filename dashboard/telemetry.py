from dataclasses import dataclass, field
import csv
import json
import math
from pathlib import Path
import time


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    command: str | None
    unit: str
    minimum: float
    maximum: float
    interval: float = 2.0
    stale_after: float = 10.0


METRICS = (
    Metric('speed', 'Vehicle speed', 'SPEED', 'kph', 0, 300, .25, 3),
    Metric('rpm', 'Engine speed', 'RPM', 'rpm', 0, 8000, .25, 3),
    Metric('coolant', 'Coolant', 'COOLANT_TEMP', 'degC', -40, 215),
    Metric('fuel', 'Fuel level', 'FUEL_LEVEL', 'percent', 0, 100, 5, 20),
    Metric('voltage', 'ECU voltage', 'CONTROL_MODULE_VOLTAGE', 'volt', 0, 25),
    Metric('adapter_voltage', 'Adapter voltage', 'ELM_VOLTAGE', 'volt', 0, 25, 5, 20),
    Metric('oil_pressure', 'Oil pressure', None, 'psi', 0, 200),
    Metric('oil_temp', 'Oil temperature', 'OIL_TEMP', 'degC', -40, 215),
    Metric('trans_temp', 'Transmission', None, 'degC', -40, 215),
    Metric('intake_temp', 'Intake air', 'INTAKE_TEMP', 'degC', -40, 215),
    Metric('ambient_temp', 'Outside air', 'AMBIANT_AIR_TEMP', 'degC', -40, 100, 5, 20),
    Metric('load', 'Engine load', 'ENGINE_LOAD', 'percent', 0, 100),
    Metric('throttle', 'Throttle', 'THROTTLE_POS', 'percent', 0, 100),
    Metric('map', 'Manifold pressure', 'INTAKE_PRESSURE', 'kPa', 0, 255),
    Metric('runtime', 'Engine run time', 'RUN_TIME', 'second', 0, 1e8, 5, 20),
    Metric('trim_short', 'Fuel trim · short B1', 'SHORT_FUEL_TRIM_1', 'percent', -100, 100, 5, 20),
    Metric('trim_long', 'Fuel trim · long B1', 'LONG_FUEL_TRIM_1', 'percent', -100, 100, 5, 20),
)
BY_KEY = {metric.key: metric for metric in METRICS}


@dataclass(frozen=True)
class Reading:
    value: float | None = None
    state: str = 'waiting'
    timestamp: float = 0
    source: str = 'OBD-II'
    detail: str = ''

    def current(self, metric, now=None):
        now = time.monotonic() if now is None else now
        if self.state == 'ok' and now - self.timestamp > metric.stale_after:
            return Reading(None, 'stale', self.timestamp, self.source, 'Last sample expired')
        return self


def numeric_reading(metric, value, now=None, source='OBD-II'):
    now = time.monotonic() if now is None else now
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return Reading(None, 'no data', now, source, 'Invalid or missing value')
    if not metric.minimum <= value <= metric.maximum:
        return Reading(None, 'no data', now, source, 'Outside valid sensor range')
    return Reading(float(value), 'ok', now, source)


def display_value(metric, reading, units='imperial', now=None):
    reading = reading.current(metric, now)
    unit = metric.unit
    if reading.state != 'ok':
        return '—', {'degC': '°F' if units == 'imperial' else '°C',
                     'kph': 'mph' if units == 'imperial' else 'km/h',
                     'percent': '%', 'volt': 'V', 'second': 'h:m:s',
                     'psi': 'psi' if units == 'imperial' else 'kPa',
                     'kPa': 'psi' if units == 'imperial' else 'kPa'}.get(unit, unit)
    value = reading.value
    if unit == 'kph' and units == 'imperial':
        value /= 1.609344
    if unit == 'degC' and units == 'imperial':
        value = value * 9 / 5 + 32
    if unit == 'psi' and units == 'metric':
        value *= 6.894757293
    if unit == 'kPa' and units == 'imperial':
        value /= 6.894757293
    if unit == 'second':
        seconds = int(value)
        return f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}', 'h:m:s'
    suffix = {'degC': '°F' if units == 'imperial' else '°C',
              'kph': 'mph' if units == 'imperial' else 'km/h',
              'percent': '%', 'volt': 'V',
              'psi': 'psi' if units == 'imperial' else 'kPa',
              'kPa': 'psi' if units == 'imperial' else 'kPa'}.get(unit, unit)
    precision = 1 if metric.key in ('voltage', 'adapter_voltage', 'oil_pressure') else 0
    return f'{value:.{precision}f}', suffix


@dataclass
class Snapshot:
    readings: dict = field(default_factory=dict)
    connection: str = 'Connecting'
    detail: str = ''
    demo: bool = False
    dtcs: tuple = ()
    dtc_state: str = 'Not scanned'
    mil: bool | None = None
    diagnostic_time: float = 0
    protocol: str = ''


class Trip:
    def __init__(self):
        self.reset()

    def reset(self):
        self.km = 0.0
        self.last = None
        self.started = time.monotonic()

    def update(self, reading):
        if reading.state != 'ok' or reading.value is None:
            self.last = None
            return
        if self.last and reading.timestamp > self.last.timestamp:
            elapsed = reading.timestamp - self.last.timestamp
            if elapsed <= 3:
                self.km += (self.last.value + reading.value) / 2 * elapsed / 3600
        if self.last is None or reading.timestamp >= self.last.timestamp:
            self.last = reading


class ExternalSensors:
    ALLOWED = {'oil_pressure', 'trans_temp', 'oil_temp', 'ambient_temp'}

    def __init__(self, path=None):
        self.path = Path(path) if path else None

    def read(self, now=None, wall_time=None):
        now = time.monotonic() if now is None else now
        wall_time = time.time() if wall_time is None else wall_time
        if self.path is None:
            return {}
        result = {key: Reading(None, 'no data', now, 'External sensor') for key in self.ALLOWED}
        try:
            if self.path.stat().st_size > 65536:
                raise ValueError('Sensor file too large')
            data = json.loads(self.path.read_text(encoding='utf-8'))
            stamp = data.get('timestamp')
            if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
                raise ValueError('Missing sensor timestamp')
            age = wall_time - stamp
            if age < -2 or age > 5:
                return {key: Reading(None, 'stale', now, 'External sensor', 'Timestamp expired')
                        for key in self.ALLOWED}
            values = data.get('values', {})
            for key in self.ALLOWED:
                if key in values:
                    result[key] = numeric_reading(BY_KEY[key], values[key], now - max(0, age), 'External sensor')
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        return result


class Recorder:
    def __init__(self, path):
        self.file = Path(path).open('x', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['utc_epoch', 'mode', 'connection', 'metric', 'value', 'unit', 'state', 'source'])

    def write(self, snapshot):
        for metric in METRICS:
            reading = snapshot.readings.get(metric.key, Reading()).current(metric)
            self.writer.writerow([time.time(), 'demo' if snapshot.demo else 'live', snapshot.connection,
                                  metric.key, '' if reading.state != 'ok' else reading.value,
                                  metric.unit, reading.state, reading.source])
        self.file.flush()

    def close(self):
        self.file.close()
