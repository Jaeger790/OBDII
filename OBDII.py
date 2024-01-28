import obd
from obd import commands
from Main_Window import Main_Window
import tkinter as tk
from Engine_Commands import Engine_Commands
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from pyqt_gauge import RPMGauge

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RPMGauge()
    window.setGeometry(600, 600, 800, 1200)
    window.setWindowTitle('Dash Gauges')
    window.setStyleSheet("background-color: rgba(65, 105, 225,.4);")
    window.show()
    sys.exit(app.exec_())    

    # root = tk.Tk()
    # main_window = Main_Window(root)
    # commands = Engine_Commands()
    # main_window.update_data()
    # root.mainloop()
    


   



    


