from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel 
import sys
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
        self.gauge_width = 500
        self.gauge_height = 150
        
        # Create RPM label
        self.rpm_label = QLabel(self)
        font = QFont("Fira Code", 32, QFont.Bold)
        font.setPointSize(32)  # Set the desired font size
        self.rpm_label.setFont(font)
        self.rpm_label.setStyleSheet("""
            color: white; 
            background-color: rgba(0,0,0,0);
        """)
        self.rpm_label.setAlignment(Qt.AlignCenter)
        self.rpm_label.setFixedHeight(50)
        self.rpm_label.setFixedWidth(300)
        self.rpm_label.setText(str(self.rpm_value))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        #calculate rpm gauge percentage
        fill_percentage = self.rpm_value / self.max_rpm
        fill_width = fill_percentage * self.gauge_width

        # Draw gauge outline
        gauge_rect = QRectF(0, 0, self.gauge_width, self.gauge_height)
        bg_brush = QBrush(QColor(0, 0, 0,255))
        painter.setBrush(bg_brush)
        painter.drawRect(gauge_rect)

        # Draw fill bar
        fill_rect = QRectF(0, 0, fill_width, self.gauge_height)
        fill_brush = QBrush(QColor(0, 255, 0, 255))
        fill_brush.setStyle(Qt.Dense4Pattern)
        painter.setBrush(fill_brush)


    #update the gauge data
    def update_RPM_gauge(self):

        # Update RPM value
        rpm_value = self.commands.get_engine_rpm()
        if rpm_value is not None :
            self.rpm_value = rpm_value.magnitude
            self.rpm_label.setText(str(self.rpm_value))
            self.update()
        else:
            self.rpm_value = 0
            self.update()
            
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RPMGauge()
    
    window.setFixedSize(800, 600)
    window.show()
    
    sys.exit(app.exec_())