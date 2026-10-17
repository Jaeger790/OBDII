import argparse
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description='2006 Ram 1500 digital dashboard')
    parser.add_argument('--demo', action='store_true', help='Simulated data; no adapter connection')
    parser.add_argument('--port', default=os.getenv('OBD_PORT'))
    parser.add_argument('--baudrate', type=int)
    parser.add_argument('--protocol', help='python-OBD protocol ID; omitted for automatic detection')
    parser.add_argument('--units', choices=('imperial', 'metric'), default='imperial')
    parser.add_argument('--vehicle', default='2006 RAM 1500 · 4.7L V8')
    parser.add_argument('--fullscreen', action='store_true')
    parser.add_argument('--sensors', type=Path, help='Timestamped external-sensor JSON file')
    parser.add_argument('--record', type=Path, help='New CSV file; existing files are never overwritten')
    parser.add_argument('--screenshot', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.baudrate is not None and args.baudrate <= 0:
        parser.error('--baudrate must be positive')
    if args.record and args.record.exists():
        parser.error('--record must name a new file')
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication
    from dashboard.transport import DemoTransport, ObdTransport
    from dashboard.worker import TelemetryWorker
    from dashboard.ui import Dashboard

    app = QApplication([sys.argv[0]])
    factory = DemoTransport if args.demo else lambda: ObdTransport(args.port, args.baudrate, args.protocol)
    worker = TelemetryWorker(factory, args.demo, args.sensors, args.record)
    window = Dashboard(worker, args.units, args.vehicle)
    window.showFullScreen() if args.fullscreen else window.show()
    worker.start()
    if args.screenshot:
        def capture():
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            window.grab().save(str(args.screenshot))
            window.close()
        QTimer.singleShot(3000, capture)
    return app.exec_()


if __name__ == '__main__':
    raise SystemExit(main())
