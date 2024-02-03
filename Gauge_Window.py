from PyQt5.QtCore import Qt, QTimer,QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QGridLayout
from Fuel_Bar import Fuel_Bar
from RPM_Gauge import RPMGauge
import sys


class Gauge_Window(QWidget):
    def __init__(self):
        super().__init__()
        app = QApplication(sys.argv)
        self.setWindowTitle("OBDII")
        self.setGeometry(600, 600, 800, 1200)
        self.setStyleSheet("background-color: rgba(65, 105, 225,.4);")
        
        #initialize the fuel bar and rpm gauge and add them to the window using a grid layout
        self.fuel_bar = Fuel_Bar()
        self.rpm_gauge = RPMGauge()

        self.layout = QGridLayout()
        self.layout.addWidget(self.fuel_bar, 0, 0)
        self.layout.addWidget(self.rpm_gauge, 1, 0)
        self.setLayout(self.layout)


                     
            

        self.show()
        sys.exit(app.exec_())  




