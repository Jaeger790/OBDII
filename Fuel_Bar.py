from PyQt5.QtCore import Qt, QTimer,QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QVBoxLayout, QGridLayout
import math, sys
from Engine_Commands import Engine_Commands


class Fuel_Bar(QWidget):


    def __init__ (self, parent=None):
        super().__init__(parent)
        self.Fuel_Bar_Width = 500
        self.Fuel_Bar_Height = 100
        self.fuel_value = 0
        self.max_fuel = 100
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fuel_gauge)
        self.timer.start(300)
        self.commands = Engine_Commands()
        self.fuel_bar_font = QFont()
        self.fuel_bar_font.setPixelSize(18)


        
        #fuel level background bar
        self.fuel_level_bg = QLabel(self)
        self.fuel_level_bg.setFixedWidth(self.Fuel_Bar_Width)
        self.fuel_level_bg.setFixedHeight(self.Fuel_Bar_Height)
        self.fuel_level_bg.setStyleSheet("background-color: black; border: 1px solid black;")

        #fuel bar
        self.fuel_level_bar = QLabel(self)
        self.fuel_level_bar.setFixedWidth(self.Fuel_Bar_Width)
        self.fuel_level_bar.setFixedHeight(self.Fuel_Bar_Height)
        self.fuel_level_bar.setStyleSheet("background-color: green; border: 1px solid black;")
        

        #Create a label to display the fuel level

        self.fuel_level_label = QLabel(self)
        self.fuel_level_label.setFixedWidth(50)
        self.fuel_level_label.setFixedHeight(40)
        self.fuel_level_label.setAlignment(Qt.AlignCenter)
        self.fuel_level_label.setStyleSheet("color: green; background-color: black; border: 2px solid black;")
        self.fuel_level_label.setText(str(self.fuel_value))
        self.fuel_level_label.setFont(self.fuel_bar_font)
        
        #stack the fuel bar and fuel level label and center the label within the fuel bar
        self.layout = QGridLayout()
        self.layout.addWidget(self.fuel_level_bg, 0, 0)
        self.layout.addWidget(self.fuel_level_bar, 0, 0)
        self.layout.addWidget(self.fuel_level_label, 0, 0)
        self.setLayout(self.layout)


        #change fuel bar color if low
    def low_fuel(self, fuel_level):
        fuel_level = self.fuel_value
        
        if fuel_level <= 25:
            self.fuel_level_bar.setStyleSheet("background-color: red; border: 1px solid black;")
            self.fuel_level_label.setStyleSheet("color: red; background-color: black; border: 1px solid black;")
        else:
            self.fuel_level_label.setStyleSheet("color: white; background-color: green; border: 2px solid black;")        




    def update_fuel_gauge(self):
        # Update fuel level
        
        self.fuel_value = self.commands.get_fuel_level()
        if self.fuel_value is not None :
            # Update fuel level bar
            self.fuel_level_width = int((self.fuel_value.magnitude / self.max_fuel) * 500)
            self.fuel_level_bar.setFixedWidth(self.fuel_level_width)
            #update text
            self.fuel_level_label.setText(str(self.fuel_value.magnitude))
            self.low_fuel()
            self.update(self.fuel_value.magnitude)
        else:
            self.fuel_value = 0
            self.fuel_level_width = int((self.fuel_value / self.max_fuel) * 500)
            self.fuel_level_bar.setFixedWidth(self.fuel_level_width)

            self.low_fuel(self.fuel_value)

            self.fuel_level_bar.setFixedWidth(self.fuel_value)
            self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Fuel_Bar()
    window.show()
    
    sys.exit(app.exec_())
