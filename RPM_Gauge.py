from PyQt5.QtCore import Qt, QTimer,QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QVBoxLayout
import math, sys
from Engine_Commands import Engine_Commands

class RPMGauge(QWidget):
    

    def __init__(self):
        super().__init__()
        self.rpm_value = 0
        self.max_rpm = 7000  
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_RPM_gauge)
        self.timer.start(300)  # Update every 1/3 second
        self.commands = Engine_Commands()


    # Trigger the RPM gauge to be drawn 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
    
        self.draw_gauge(painter)
        
    #Draw the RPM gauge
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

        #fill the rpm gauge with color based on rpm value
        if self.rpm_value < 1000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 2000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 3000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 4000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 5000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 6000:
            painter.setBrush(QColor(0, 255, 0))
        elif self.rpm_value < 7000:
            painter.setBrush(QColor(0, 255, 0))
        else:
            painter.setBrush(QColor(0, 255, 0))
        
# Draw RPM arc
        painter.setPen(QPen(QColor(0, 255, 0), 10))
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius),
                    start_angle * 16, self.rpm_value * 16)
        
# Draw RPM ticks
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.NoBrush)
        num_ticks = 8
        tick_length = 20
        for i in range(num_ticks):
            angle = start_angle + i * (span_angle / (num_ticks - 1))
            x1 = center.x() + int((radius - tick_length) * math.cos(math.radians(90 - angle)))
            y1 = center.y() - int((radius - tick_length) * math.sin(math.radians(90 - angle)))
            x2 = center.x() + int(radius * math.cos(math.radians(90 - angle)))
            y2 = center.y() - int(radius * math.sin(math.radians(90 - angle)))
            painter.drawLine(x1, y1, x2, y2)
            
# Draw RPM needle


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
    


    #update the gauge data
    def update_RPM_gauge(self):


        # Update RPM value
        self.rpm_value = self.commands.get_engine_rpm()
        if self.rpm_value is not None :
            self.rpm_value = self.commands.get_engine_rpm().magnitude
            self.update()
        else:
            self.rpm_value = 0
