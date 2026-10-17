import math
import time

from dashboard.telemetry import METRICS, BY_KEY, Reading, Snapshot, numeric_reading


class DemoTransport:
    def __init__(self):
        self.started = time.monotonic()
        self.protocol = 'Simulated · no vehicle connection'

    def connect(self):
        return True

    def sample(self, metric):
        t = time.monotonic() - self.started
        speed = max(0, 75 + 20 * math.sin(t / 12))
        values = {'speed': speed, 'rpm': 1750 + 650 * math.sin(t / 12), 'coolant': 93,
                  'fuel': 63, 'voltage': 14.1, 'adapter_voltage': 14.0, 'oil_pressure': 46,
                  'oil_temp': 100, 'trans_temp': 83, 'intake_temp': 31, 'ambient_temp': 23,
                  'load': 38 + 10 * math.sin(t / 12), 'throttle': 22, 'map': 48,
                  'runtime': 1640 + t, 'trim_short': 2.3, 'trim_long': -1.2}
        return numeric_reading(metric, values[metric.key], source='DEMO')

    def diagnostics(self):
        return (), 'Demo · no codes', False

    def close(self):
        pass


class ObdTransport:
    def __init__(self, port=None, baudrate=None, protocol=None, timeout=1):
        self.options = dict(portstr=port, baudrate=baudrate, protocol=protocol, timeout=timeout)
        self.connection = None
        self.protocol = ''
        self.obd = None

    def connect(self):
        import obd
        self.obd = obd
        self.close()
        self.connection = obd.OBD(**self.options)
        if not self.connection.is_connected():
            self.close()
            return False
        self.protocol = str(self.connection.protocol_name())
        return True

    def sample(self, metric):
        now = time.monotonic()
        if metric.command is None:
            return Reading(None, 'unconfigured', now, 'External sensor', 'Requires verified sensor data')
        command = getattr(self.obd.commands, metric.command, None)
        if command is None or not self.connection.supports(command):
            return Reading(None, 'unsupported', now)
        response = self.connection.query(command)
        if response.is_null():
            return Reading(None, 'no data', now)
        try:
            value = response.value.to(metric.unit).magnitude
            return numeric_reading(metric, float(value), source='Adapter' if metric.key == 'adapter_voltage' else 'OBD-II')
        except (ValueError, TypeError, AttributeError):
            return Reading(None, 'no data', now, detail='Unable to convert response units')

    def diagnostics(self):
        command = self.obd.commands.GET_DTC
        codes = self.connection.query(command) if self.connection.supports(command) else None
        if codes is None or codes.is_null():
            dtcs, state = (), 'Unavailable · no diagnostic response'
        else:
            dtcs = tuple((str(code), str(description or 'No description')) for code, description in codes.value)
            state = f'{len(dtcs)} stored code(s)'
        mil = None
        status = self.obd.commands.STATUS
        if self.connection.supports(status):
            response = self.connection.query(status)
            if not response.is_null():
                mil = bool(response.value.MIL)
        return dtcs, state, mil

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
