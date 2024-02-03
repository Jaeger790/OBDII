from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QGridLayout, QWidget, QVBoxLayout
from UI.Fuel_Bar import Fuel_Bar
from UI.RPM_Gauge import RPMGauge
from UI.DTC_Window import DTC_Window
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




