import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import time
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from dashboard.telemetry import BY_KEY, Snapshot, Reading, numeric_reading
from dashboard.transport import DemoTransport
from dashboard.worker import TelemetryWorker
from dashboard.ui import Dashboard


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_demo_worker_updates_and_stops(self):
        worker = TelemetryWorker(DemoTransport, demo=True)
        window = Dashboard(worker)
        window.show()
        worker.start()
        QTest.qWait(800)
        window.refresh()
        self.assertIsNotNone(window.snapshot)
        self.assertIn('SIMULATED', window.connection.text())
        self.assertNotEqual(window.speed.number, '—')
        worker.stop()
        self.assertTrue(worker.wait(3000))
        window.close()

    def test_stale_values_hide_on_all_screens_and_disconnect_clears_mil(self):
        worker = TelemetryWorker(DemoTransport)
        window = Dashboard(worker)
        window.receive(Snapshot(readings={'speed': numeric_reading(BY_KEY['speed'], 80, time.monotonic()-10)},
                                connection='Disconnected', mil=None))
        window.refresh()
        self.assertEqual(window.speed.number, '—')
        self.assertIn('UNKNOWN', window.mil.text())
        self.assertEqual(window.sensor_table.item(0, 2).text(), 'stale')
        window.close()

    def test_worker_handles_connection_failure_and_cooperative_stop(self):
        class FailedTransport:
            def connect(self): return False
            def close(self): pass
        worker = TelemetryWorker(FailedTransport)
        snapshots = []
        worker.updated.connect(snapshots.append)
        worker.start()
        QTest.qWait(200)
        worker.stop()
        self.assertTrue(worker.wait(3000))
        self.app.processEvents()
        self.assertTrue(any(s.connection == 'Disconnected' for s in snapshots))
