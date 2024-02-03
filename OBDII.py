from UI.DTC_Window import DTC_Window
from UI.Gauge_Window import Gauge_Window
import sys
from PyQt5.QtWidgets import QApplication




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Gauge_Window()

    window.show()    
    sys.exit(app.exec_())

  


    


   



    


