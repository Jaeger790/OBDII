from PyQt5.QtCore import Qt, QTimer,QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLabel 
import math, sys
from Engine_Commands import Engine_Commands

class RPMGauge(QWidget):
    

    def __init__(self, parent=None):
        super().__init__(parent)
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
        font = QFont()
        font.setPointSize(32)  # Set the desired font size
        self.rpm_label.setFont(font)
        self.rpm_label.setAlignment(Qt.AlignCenter)
        self.rpm_label.setFixedHeight(50)
        self.rpm_label.setFixedWidth(100)
        self.rpm_label.setText(str(self.rpm_value))


    # Draw gauge outline
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        #calculate rpm gauge percentage
        fill_percentage = self.rpm_value / self.max_rpm
        fill_width = fill_percentage * self.gauge_width


        # Draw fill bar
        fill_rect = QRectF(0, 0, fill_width, self.gauge_height)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(150, 150, 0))
        painter.drawRect(fill_rect)


        # Draw gauge outline
        gauge_rect = QRectF(0, 0, self.gauge_width, self.gauge_height)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(gauge_rect)        


    #update the gauge data
    def update_RPM_gauge(self):

        # Update RPM value
        rpm_value = self.commands.get_engine_rpm()
        print(f'rpm value before none check: {rpm_value}')
        if rpm_value is not None :
            self.rpm_value = rpm_value.magnitude
            self.paintEvent(self, event = None)
            print(f"RPM value after none check: {rpm_value.magnitude}")  # Debug print

            #calculate rpm gauge percentage
            self.rpm_label.setText(self.rpm_value)
            self.update()
        else:
            self.rpm_value = 0
            print("No rpm value")  # Debug print
            self.update()
            
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RPMGauge()
    window.show()
    
    sys.exit(app.exec_())