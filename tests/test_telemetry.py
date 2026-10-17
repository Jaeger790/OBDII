import csv
import json
from pathlib import Path
import tempfile
import time
import unittest

from dashboard.telemetry import BY_KEY, Reading, Snapshot, numeric_reading, display_value, Trip, ExternalSensors, Recorder
from tools.sensor_bridge import publish


class TelemetryTests(unittest.TestCase):
    def test_unit_conversion(self):
        now = time.monotonic()
        self.assertEqual(display_value(BY_KEY['speed'], numeric_reading(BY_KEY['speed'], 160.9344, now), 'imperial')[0], '100')
        self.assertEqual(display_value(BY_KEY['coolant'], numeric_reading(BY_KEY['coolant'], 100, now), 'imperial'), ('212', '°F'))
        self.assertEqual(display_value(BY_KEY['coolant'], numeric_reading(BY_KEY['coolant'], 100, now), 'metric'), ('100', '°C'))

    def test_pressure_conversion(self):
        pressure = numeric_reading(BY_KEY['oil_pressure'], 10)
        self.assertEqual(display_value(BY_KEY['oil_pressure'], pressure, 'metric'), ('68.9', 'kPa'))
        self.assertEqual(display_value(BY_KEY['map'], numeric_reading(BY_KEY['map'], 100), 'imperial'), ('15', 'psi'))

    def test_zero_is_valid_but_bad_values_are_not(self):
        metric = BY_KEY['speed']
        self.assertEqual(numeric_reading(metric, 0).state, 'ok')
        for value in (None, True, '80', float('nan'), float('inf'), -1, 301):
            self.assertEqual(numeric_reading(metric, value).state, 'no data')

    def test_stale_reading_is_not_displayed_as_current(self):
        metric = BY_KEY['speed']
        reading = numeric_reading(metric, 80, now=100)
        self.assertEqual(reading.current(metric, 104).state, 'stale')
        self.assertEqual(display_value(metric, reading, now=104)[0], '—')
        self.assertEqual(reading.current(metric, 102).state, 'ok')

    def test_trip_uses_fresh_samples_and_never_fills_connection_gaps(self):
        trip = Trip()
        for timestamp in range(101, 111):
            trip.update(numeric_reading(BY_KEY['speed'], 36, timestamp))
        self.assertAlmostEqual(trip.km, .09)
        trip.update(numeric_reading(BY_KEY['speed'], 36, 200))
        self.assertAlmostEqual(trip.km, .09)
        trip.update(Reading(None, 'disconnected'))
        trip.update(numeric_reading(BY_KEY['speed'], 100, 201))
        self.assertAlmostEqual(trip.km, .09)
        trip.reset()
        self.assertEqual(trip.km, 0)

    def test_external_values_require_timestamp_and_expire(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sensors.json'
            path.write_text(json.dumps({'timestamp': 1000, 'values': {'oil_pressure': 44, 'trans_temp': 80}}))
            sensors = ExternalSensors(path)
            data = sensors.read(now=50, wall_time=1001)
            self.assertEqual(data['oil_pressure'].value, 44)
            self.assertEqual(data['oil_pressure'].timestamp, 49)
            self.assertEqual(sensors.read(now=56, wall_time=1006)['oil_pressure'].state, 'stale')
            self.assertEqual(sensors.read(now=40, wall_time=995)['oil_pressure'].state, 'stale')
            path.write_text('{bad json')
            self.assertEqual(sensors.read()['oil_pressure'].state, 'no data')
            path.write_text(json.dumps({'timestamp': None, 'values': {'oil_pressure': 44}}))
            self.assertEqual(sensors.read()['oil_pressure'].state, 'no data')

    def test_external_bridge_checks_ranges_and_writes_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sensors.json'
            publish('{"oil_pressure": 40, "trans_temp": 80}', path)
            self.assertEqual(ExternalSensors(path).read()['oil_pressure'].value, 40)
            before = path.read_text()
            for line in ('{"oil_pressure": true}', '{"oil_pressure": -1}', '{"rpm": 500}', 'null'):
                with self.assertRaises(ValueError):
                    publish(line, path)
                self.assertEqual(path.read_text(), before)

    def test_csv_records_missing_data_without_false_zero_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'trip.csv'
            recorder = Recorder(path)
            recorder.write(Snapshot(readings={'speed': Reading(None, 'unsupported')}, demo=True))
            recorder.close()
            with path.open() as file:
                rows = list(csv.DictReader(file))
            speed = next(row for row in rows if row['metric'] == 'speed')
            self.assertEqual(speed['value'], '')
            self.assertEqual(speed['mode'], 'demo')
            with self.assertRaises(FileExistsError):
                Recorder(path)
