import math
import time
from datetime import datetime

from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QComboBox,
)

from dashboard.telemetry import METRICS, BY_KEY, Reading, Trip, display_value

BG = '#090f16'
PANEL = '#111c27'
TEXT = '#eef5fb'
MUTED = '#90a5b8'
ACCENT = '#f0a34a'


class Dial(QWidget):
    def __init__(self, title, maximum, step, accent=ACCENT):
        super().__init__()
        self.title = title
        self.maximum = maximum
        self.step = step
        self.accent = accent
        self.number = '—'
        self.unit = ''
        self.value = None
        self.state = 'waiting'
        self.setMinimumSize(270, 245)

    def set_reading(self, metric, reading, units):
        current = reading.current(metric)
        self.number, self.unit = display_value(metric, current, units)
        self.state = current.state
        self.value = current.value
        if metric.key == 'speed':
            self.maximum = 140 if units == 'imperial' else 220
            self.step = 20
            if self.value is not None and units == 'imperial':
                self.value /= 1.609344
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        scale = min(self.width() / 390, self.height() / 320)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(scale, scale)
        ring = QRectF(-128, -128, 256, 256)
        painter.setPen(QPen(QColor('#243645'), 14, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(ring, -45 * 16, 270 * 16)
        if self.value is not None and self.state == 'ok':
            fraction = min(1, max(0, self.value / self.maximum))
            painter.setPen(QPen(QColor(self.accent), 14, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(ring, 225 * 16, int(-270 * 16 * fraction))
        painter.setFont(QFont('DejaVu Sans', 10))
        for number in range(0, self.maximum + 1, self.step):
            angle = math.radians(135 + 270 * number / self.maximum)
            x, y = math.cos(angle), math.sin(angle)
            painter.setPen(QPen(QColor(MUTED), 2))
            painter.drawLine(int(x * 108), int(y * 108), int(x * 115), int(y * 115))
            label = str(number // 1000) if self.maximum == 7000 else str(number)
            painter.drawText(QRectF(x * 91 - 18, y * 91 - 10, 36, 20), Qt.AlignCenter, label)
        painter.setPen(QColor(TEXT))
        painter.setFont(QFont('DejaVu Sans', 47 if self.title == 'SPEED' else 39, QFont.Bold))
        painter.drawText(QRectF(-112, -49, 224, 78), Qt.AlignCenter, self.number)
        painter.setPen(QColor(MUTED))
        painter.setFont(QFont('DejaVu Sans', 12))
        painter.drawText(QRectF(-110, 28, 220, 26), Qt.AlignCenter, self.unit)
        painter.setFont(QFont('DejaVu Sans', 11, QFont.Bold))
        painter.drawText(QRectF(-130, 112, 260, 28), Qt.AlignCenter, self.title)
        if self.state != 'ok':
            painter.setPen(QColor(ACCENT))
            painter.setFont(QFont('DejaVu Sans', 10))
            painter.drawText(QRectF(-130, 78, 260, 24), Qt.AlignCenter, self.state.upper())


class Card(QFrame):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.setObjectName('card')
        self.setMinimumHeight(94)
        box = QVBoxLayout(self)
        box.setContentsMargins(16, 10, 16, 10)
        self.title = QLabel(BY_KEY[key].label.upper())
        self.title.setObjectName('cardTitle')
        self.value = QLabel('—')
        self.value.setObjectName('cardValue')
        self.status = QLabel('Waiting')
        self.status.setObjectName('muted')
        box.addWidget(self.title)
        box.addWidget(self.value)
        box.addWidget(self.status)

    def refresh(self, reading, units):
        metric = BY_KEY[self.key]
        current = reading.current(metric)
        text, unit = display_value(metric, current, units)
        self.value.setText(f'{text} <span style="font-size:14px;color:{MUTED}">{unit}</span>')
        state = current.source if current.state == 'ok' else current.state.capitalize()
        self.status.setText(state)
        self.setToolTip(current.detail or f'{metric.label} · {current.source}')


class Dashboard(QMainWindow):
    def __init__(self, worker, units='imperial', vehicle='2006 RAM 1500 · 4.7L V8'):
        super().__init__()
        self.worker = worker
        self.units = units
        self.snapshot = None
        self.trip = Trip()
        self.last_speed_stamp = None
        self.closing = False
        self.setWindowTitle('Ram 1500 · Digital Dashboard')
        self.resize(1280, 820)
        self.setMinimumSize(950, 680)
        self.setStyleSheet(f'''
            QWidget {{background:{BG};color:{TEXT};font-family:"DejaVu Sans";font-size:13px;}}
            QFrame#card {{background:{PANEL};border:1px solid #263544;border-radius:10px;}}
            QFrame#card QLabel {{background:transparent;}}
            QLabel#cardTitle {{color:{MUTED};font-size:10px;font-weight:600;}}
            QLabel#cardValue {{font-size:28px;font-weight:700;}}
            QLabel#muted {{color:{MUTED};font-size:11px;}}
            QPushButton,QComboBox {{background:#192936;border:1px solid #334859;border-radius:5px;padding:8px 12px;}}
            QPushButton:hover {{border-color:{ACCENT};}}
            QTabWidget::pane {{border:0;}}
            QTabBar::tab {{padding:11px 20px;color:{MUTED};border-bottom:2px solid transparent;}}
            QTabBar::tab:selected {{color:{ACCENT};border-bottom:2px solid {ACCENT};}}
            QTableWidget {{background:{PANEL};gridline-color:#263544;border:0;}}
            QHeaderView::section {{background:#192936;color:{MUTED};padding:9px;border:0;}}
        ''')
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 16, 24, 16)
        self.setCentralWidget(root)
        header = QHBoxLayout()
        title = QLabel('RAM <span style="color:#f0a34a">/</span> 1500')
        title.setStyleSheet('font-size:25px;font-weight:800;letter-spacing:3px;')
        header.addWidget(title)
        header.addWidget(QLabel(vehicle))
        header.addStretch()
        self.connection = QLabel('CONNECTING')
        header.addWidget(self.connection)
        self.clock = QLabel()
        self.clock.setStyleSheet('font-size:24px;font-weight:600;')
        header.addWidget(self.clock)
        layout.addLayout(header)
        self.notice = QLabel('Waiting for adapter. Demo mode never connects to the truck.')
        self.notice.setObjectName('muted')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        drive = QWidget()
        grid = QGridLayout(drive)
        grid.setContentsMargins(0, 12, 0, 8)
        grid.setSpacing(12)
        self.rpm = Dial('ENGINE RPM', 7000, 1000, '#78bfd0')
        self.speed = Dial('SPEED', 140, 20)
        grid.addWidget(self.rpm, 0, 0, 1, 2)
        grid.addWidget(self.speed, 0, 2, 1, 2)
        self.cards = {}
        for index, key in enumerate(('coolant', 'fuel', 'oil_pressure', 'voltage', 'oil_temp', 'trans_temp', 'intake_temp', 'ambient_temp')):
            card = Card(key)
            self.cards[key] = card
            grid.addWidget(card, 1 + index // 4, index % 4)
        grid.setRowStretch(0, 1)
        for column in range(4):
            grid.setColumnStretch(column, 1)
        self.tabs.addTab(drive, 'DRIVE')
        power = QWidget()
        power_grid = QGridLayout(power)
        for index, key in enumerate(('load', 'throttle', 'map', 'runtime', 'adapter_voltage', 'trim_short', 'trim_long')):
            card = Card(key)
            self.cards[key] = card
            power_grid.addWidget(card, index // 3, index % 3)
        note = QLabel('Oil pressure and transmission temperature need verified external sensor data.\n'
                      'Gear, turn signals, ABS, airbag state and factory odometer are not inferred from generic OBD-II.')
        note.setWordWrap(True)
        note.setObjectName('muted')
        power_grid.addWidget(note, 3, 0, 1, 3)
        self.tabs.addTab(power, 'POWERTRAIN')
        diagnostics = QWidget()
        diagnostic_layout = QVBoxLayout(diagnostics)
        self.diagnostic_label = QLabel('Stored engine codes · not scanned')
        diagnostic_layout.addWidget(self.diagnostic_label)
        self.dtc_table = self.table(('Code', 'Description'))
        diagnostic_layout.addWidget(self.dtc_table)
        scan = QPushButton('Read engine trouble codes')
        scan.clicked.connect(worker.request_scan)
        diagnostic_layout.addWidget(scan)
        diagnostic_layout.addWidget(QLabel('Read-only diagnostics. This app does not clear codes or send actuator commands.'))
        self.tabs.addTab(diagnostics, 'DIAGNOSTICS')
        self.sensor_table = self.table(('Instrument', 'Value', 'State', 'Source', 'Sample age'))
        self.sensor_table.setRowCount(len(METRICS))
        self.tabs.addTab(self.sensor_table, 'SENSOR STATUS')
        footer = QHBoxLayout()
        self.mil = QLabel('CHECK ENGINE · UNKNOWN')
        self.trip_label = QLabel()
        footer.addWidget(self.mil)
        footer.addStretch()
        footer.addWidget(self.trip_label)
        reset = QPushButton('Reset trip')
        reset.clicked.connect(self.trip.reset)
        footer.addWidget(reset)
        chooser = QComboBox()
        chooser.addItems(('Imperial', 'Metric'))
        chooser.setCurrentIndex(0 if units == 'imperial' else 1)
        chooser.currentIndexChanged.connect(lambda i: setattr(self, 'units', 'imperial' if i == 0 else 'metric'))
        footer.addWidget(chooser)
        reconnect = QPushButton('Reconnect')
        reconnect.clicked.connect(worker.request_reconnect)
        footer.addWidget(reconnect)
        full = QPushButton('Full screen')
        full.clicked.connect(self.toggle_fullscreen)
        footer.addWidget(full)
        layout.addLayout(footer)
        self.record_label = QLabel('CSV logging enabled' if worker.record_path else 'SESSION TRIP · speed-integrated estimate · F11 full screen / Esc windowed')
        self.record_label.setObjectName('muted')
        layout.addWidget(self.record_label)
        worker.updated.connect(self.receive)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(200)
        self.refresh()

    @staticmethod
    def table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def receive(self, snapshot):
        self.snapshot = snapshot
        reading = snapshot.readings.get('speed', Reading())
        if reading.timestamp != self.last_speed_stamp or reading.state != 'ok':
            self.trip.update(reading.current(BY_KEY['speed']))
            self.last_speed_stamp = reading.timestamp

    def refresh(self):
        self.clock.setText(datetime.now().strftime('%I:%M:%S %p'))
        elapsed = int(time.monotonic() - self.trip.started)
        distance = self.trip.km / 1.609344 if self.units == 'imperial' else self.trip.km
        self.trip_label.setText(f'TRIP {distance:.1f} {"mi" if self.units == "imperial" else "km"}  /  {elapsed // 3600:02}:{elapsed // 60 % 60:02}:{elapsed % 60:02}')
        if self.snapshot is None:
            return
        snap = self.snapshot
        self.connection.setText('DEMO · SIMULATED' if snap.demo else snap.connection.upper())
        self.connection.setStyleSheet(f'color:{ACCENT if snap.demo or snap.connection != "Connected" else "#73cfad"};font-weight:700;')
        self.notice.setText('SIMULATED DATA · no vehicle connected' if snap.demo else snap.detail or snap.protocol or 'Waiting for data')
        self.rpm.set_reading(BY_KEY['rpm'], snap.readings.get('rpm', Reading()), self.units)
        self.speed.set_reading(BY_KEY['speed'], snap.readings.get('speed', Reading()), self.units)
        for key, card in self.cards.items():
            card.refresh(snap.readings.get(key, Reading()), self.units)
        mil = snap.mil if time.monotonic() - snap.diagnostic_time < 40 else None
        self.mil.setText('CHECK ENGINE · ' + ('ON' if mil is True else 'OFF' if mil is False else 'UNKNOWN'))
        self.mil.setStyleSheet(f'color:{"#ff937b" if mil else MUTED};font-weight:700;')
        fresh_diagnostics = time.monotonic() - snap.diagnostic_time < 40 and snap.connection in ('Connected', 'DEMO')
        self.diagnostic_label.setText('Stored engine codes · ' + (snap.dtc_state if fresh_diagnostics else 'Unavailable · stale or disconnected'))
        dtcs = snap.dtcs if fresh_diagnostics else ()
        self.dtc_table.setRowCount(len(dtcs))
        for row, pair in enumerate(dtcs):
            for column, value in enumerate(pair):
                self.dtc_table.setItem(row, column, QTableWidgetItem(value))
        for row, metric in enumerate(METRICS):
            reading = snap.readings.get(metric.key, Reading()).current(metric)
            value, unit = display_value(metric, reading, self.units)
            age = max(0, time.monotonic() - reading.timestamp) if reading.timestamp else None
            cells = (metric.label, f'{value} {unit}', reading.state, reading.source,
                     f'{age:.1f}s' if age is not None else '—')
            for column, cell in enumerate(cells):
                self.sensor_table.setItem(row, column, QTableWidgetItem(cell))

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            self.showNormal()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self.worker.stop()
        if self.worker.isRunning():
            event.ignore()
            self.notice.setText('Closing adapter connection…')
            QTimer.singleShot(100, self.close)
        else:
            event.accept()
