import time
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from dashboard.telemetry import BY_KEY
from dashboard.transport import ObdTransport, DemoTransport


class Quantity:
    def __init__(self, value):
        self.value = value

    def to(self, unit):
        return SimpleNamespace(magnitude=self.value)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.transport = ObdTransport()
        self.transport.obd = SimpleNamespace(commands=SimpleNamespace(SPEED='speed', GET_DTC='dtc', STATUS='status'))
        self.transport.connection = MagicMock()
        self.transport.connection.supports.return_value = True

    def test_missing_oil_pressure_does_not_send_invented_pid(self):
        reading = self.transport.sample(BY_KEY['oil_pressure'])
        self.assertEqual(reading.state, 'unconfigured')
        self.transport.connection.query.assert_not_called()

    def test_unsupported_command_is_not_forced(self):
        self.transport.connection.supports.return_value = False
        self.assertEqual(self.transport.sample(BY_KEY['speed']).state, 'unsupported')
        self.transport.connection.query.assert_not_called()

    def test_numeric_null_and_invalid_response(self):
        response = MagicMock()
        response.is_null.return_value = False
        response.value = Quantity(80)
        self.transport.connection.query.return_value = response
        self.assertEqual(self.transport.sample(BY_KEY['speed']).value, 80)
        response.is_null.return_value = True
        self.assertEqual(self.transport.sample(BY_KEY['speed']).state, 'no data')
        response.is_null.return_value = False
        response.value = Quantity(float('nan'))
        self.assertEqual(self.transport.sample(BY_KEY['speed']).state, 'no data')

    def test_diagnostics_return_codes_and_mil(self):
        def query(command):
            return SimpleNamespace(is_null=lambda: False, value=[('P0300', 'Random misfire')] if command == 'dtc' else SimpleNamespace(MIL=True))
        self.transport.connection.query.side_effect = query
        codes, state, mil = self.transport.diagnostics()
        self.assertEqual(codes, (('P0300', 'Random misfire'),))
        self.assertTrue(mil)
        self.assertEqual(state, '1 stored code(s)')

    def test_missing_diagnostics_are_unknown_not_clear(self):
        self.transport.connection.query.return_value.is_null.return_value = True
        codes, state, mil = self.transport.diagnostics()
        self.assertEqual(codes, ())
        self.assertIn('Unavailable', state)
        self.assertIsNone(mil)

    def test_demo_is_explicit_and_has_no_serial_connection(self):
        demo = DemoTransport()
        self.assertTrue(demo.connect())
        self.assertEqual(demo.sample(BY_KEY['oil_pressure']).source, 'DEMO')
        self.assertIn('Simulated', demo.protocol)
