from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QRectF
import math
import sys
from Engine_Commands import Engine_Commands

class RPMGauge(QWidget):
    

    def __init__(self):
        super().__init__()
        self.fuel_value = 0
        self.max_fuel = 100
        self.rpm_value = 0
        self.max_rpm = 7000  
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gauges)
        self.timer.start(300)  # Update every second (adjust as needed)
        self.commands = Engine_Commands()
        self.fuel_bar_font = QFont()
        self.fuel_bar_font.setPixelSize(18)


        #fuel level background bar
        self.fuel_level_bg = QLabel(self)
        self.fuel_level_bg.setGeometry(150, 10, 0, 0)
        self.fuel_level_bg.setFixedWidth(500)
        self.fuel_level_bg.setFixedHeight(100)
        self.fuel_level_bg.setStyleSheet("background-color: black; border: 1px solid black;")

        #fuel bar
        self.fuel_level_bar = QLabel(self)
        self.fuel_level_bar.setGeometry(150, 10,0,0)
        self.fuel_level_bar.setFixedWidth(500)
        self.fuel_level_bar.setFixedHeight(100)
        self.fuel_level_bar.setStyleSheet("background-color: green; border: 1px solid black;")
        self.fuel_level_bar.show()

        #Create a label to display the fuel level
        self.fuel_level_label = QLabel(self)
        self.fuel_level_label.setGeometry(375, 35, 15, 20)
        self.fuel_level_label.setFont(self.fuel_bar_font)
        self.fuel_level_label.setStyleSheet("color: white; background-color: black; border: 1px solid black;")
        self.fuel_level_label.setText("0")
        self.fuel_level_label.setAlignment(Qt.AlignCenter)
        self.fuel_level_label.show()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw RPM Gauge
        self.draw_gauge(painter)

    def draw_gauge(self, painter):
        painter.save()

        # Define gauge parameters
        center = self.rect().center()
        radius = min(self.width(), self.height()) / 2 - 10
        start_angle = 0
        span_angle = 360

        # Draw background arc
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawPie(QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius),
                        start_angle * 16, span_angle * 16)

        # Draw RPM value
        painter.setPen(QColor(255, 255, 255))
        rpm_font = QFont('Fira Code', 12)
        rpm_font.setBold(True)
        painter.setFont(rpm_font)
        rpm_value_rect = QRectF(center.x() - 50, center.y() + 180, 100, 30)
        painter.fillRect(rpm_value_rect, QColor(0, 255, 0))
        painter.drawText(rpm_value_rect, Qt.AlignCenter, f"{self.rpm_value} RPM")

        # Draw RPM needle
        needle_length = int(radius - 10)
        needle_angle = start_angle + span_angle * (self.rpm_value / self.max_rpm)

        # Rotate the painter around the center of the gauge
        painter.translate(center)
        painter.rotate(needle_angle)
        painter.translate(-center)

        needle_p1 = center + QPoint(0, -needle_length)
        needle_p2 = center + QPoint(0, 0)

        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(needle_p1, needle_p2)

        painter.restore()

        # Draw RPM numbers
        num_positions = 8
        rpm_increment = 1000
        rpm_values = [str(i * rpm_increment) for i in range(num_positions - 1)]

        font = QFont()
        font.setPixelSize(14)
        painter.setFont(font)
        painter.setPen(Qt.red)
        for i, rpm_value in enumerate(rpm_values):
            angle = start_angle + i * (span_angle / (num_positions - 1))
            x = center.x() + int(radius * math.cos(math.radians(90 - angle)))
            y = center.y() - int(radius * math.sin(math.radians(90 - angle)))
            painter.drawText(x, y, rpm_value)

        painter.restore()
    
    #change fuel bar color if low
    def low_fuel(self):
        if self.fuel_value < 25:
            self.fuel_level_bar.setStyleSheet("background-color: red; border: 1px solid black;")
            self.fuel_level_label.setStyleSheet("color: red; background-color: black; border: 1px solid black;")
        else:
            self.fuel_level_label.setStyleSheet("color: white; background-color: green; border: 2px solid black;")

            return False  
        

    #update the gauge data
    def update_gauges(self):
        # Update fuel level
        self.fuel_value = self.commands.get_fuel_level()
        if self.fuel_value is not None :
            # Update fuel level bar
            fuel_level_width = int((self.fuel_value / self.max_fuel) * 500)
            self.fuel_level_bar.setFixedWidth(fuel_level_width)
            self.low_fuel()
            #update text
            self.fuel_level_label.setText(str(self.fuel_value))
            self.update()
        else:
            self.fuel_value = 0    
            self.fuel_level_bar.setFixedWidth(self.fuel_value)
            self.low_fuel()

        # Update RPM value
        self.rpm_value = self.commands.get_engine_rpm()
        if self.rpm_value is not None :
            self.change_rpm_color()
        else:
            self.rpm_value = 0
