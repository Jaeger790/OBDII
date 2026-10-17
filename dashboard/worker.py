from dataclasses import replace
import threading
import time

from PyQt5.QtCore import QThread, pyqtSignal

from dashboard.telemetry import METRICS, Reading, Snapshot, ExternalSensors, Recorder


class TelemetryWorker(QThread):
    updated = pyqtSignal(object)

    def __init__(self, factory, demo=False, sensor_path=None, record_path=None):
        super().__init__()
        self.factory = factory
        self.demo = demo
        self.sensors = ExternalSensors(sensor_path)
        self.record_path = record_path
        self.stop_event = threading.Event()
        self.scan_event = threading.Event()
        self.reconnect_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def request_scan(self):
        self.scan_event.set()

    def request_reconnect(self):
        self.reconnect_event.set()

    def publish(self, snapshot):
        self.updated.emit(replace(snapshot, readings=dict(snapshot.readings)))

    def run(self):
        recorder = None
        try:
            if self.record_path:
                recorder = Recorder(self.record_path)
            while not self.stop_event.is_set():
                transport = self.factory()
                snapshot = Snapshot(demo=self.demo)
                snapshot.readings = {m.key: Reading() for m in METRICS}
                self.publish(snapshot)
                try:
                    if not transport.connect():
                        raise ConnectionError('No ECU response. Check adapter, port and ignition.')
                    snapshot.connection = 'DEMO' if self.demo else 'Connected'
                    snapshot.protocol = transport.protocol
                    due = {metric.key: 0 for metric in METRICS}
                    next_diagnostics = next_record = 0
                    empty_fast = 0
                    fast_count = 0
                    self.reconnect_event.clear()
                    while not self.stop_event.is_set() and not self.reconnect_event.is_set():
                        now = time.monotonic()
                        # Yield between serial requests so fast gauges are not stuck behind a full sensor sweep.
                        eligible = [m for m in METRICS if due[m.key] <= now]
                        if eligible:
                            fast = [m for m in eligible if m.key in ('rpm', 'speed')]
                            slow = [m for m in eligible if m.key not in ('rpm', 'speed')]
                            choices = slow if slow and (fast_count >= 2 or not fast) else fast or slow
                            metric = min(choices, key=lambda m: due[m.key])
                            fast_count = fast_count + 1 if metric.key in ('rpm', 'speed') else 0
                            reading = transport.sample(metric)
                            snapshot.readings[metric.key] = reading
                            due[metric.key] = time.monotonic() + metric.interval
                            if metric.key in ('rpm', 'speed'):
                                if reading.state == 'no data':
                                    empty_fast += 1
                                elif reading.state == 'ok':
                                    empty_fast = 0
                                if empty_fast >= 12:
                                    raise ConnectionError('ECU stopped returning speed/RPM. Reconnecting.')
                        if not self.demo:
                            external = self.sensors.read()
                            for key, reading in external.items():
                                if key in ('oil_pressure', 'trans_temp') or snapshot.readings[key].state != 'ok':
                                    snapshot.readings[key] = reading
                        if now >= next_diagnostics or self.scan_event.is_set():
                            snapshot.dtcs, snapshot.dtc_state, snapshot.mil = transport.diagnostics()
                            snapshot.diagnostic_time = time.monotonic()
                            next_diagnostics = time.monotonic() + 30
                            self.scan_event.clear()
                        self.publish(snapshot)
                        if recorder and now >= next_record:
                            recorder.write(snapshot)
                            next_record = now + 1
                        self.stop_event.wait(.02)
                except Exception as error:
                    snapshot.connection = 'Disconnected'
                    snapshot.detail = str(error)
                    snapshot.mil = None
                    snapshot.dtc_state = 'Unavailable · disconnected'
                    snapshot.dtcs = ()
                    snapshot.diagnostic_time = 0
                    snapshot.readings = {m.key: Reading(None, 'disconnected') for m in METRICS}
                    self.publish(snapshot)
                    if recorder:
                        recorder.write(snapshot)
                finally:
                    transport.close()
                self.stop_event.wait(2)
        except Exception as error:
            self.publish(Snapshot(connection='Stopped', detail=str(error), demo=self.demo))
        finally:
            if recorder:
                recorder.close()
