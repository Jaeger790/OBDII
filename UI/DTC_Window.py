import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget
class DTC_Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DTC Window")
        self.setGeometry(600, 600, 800, 1200)
        self.setStyleSheet("background-color: rgba(65, 105, 225,.4);")
        self.text_edit = QTextEdit()
        
        self.text_edit.setText("Enter DTCs here")
        self.show()
        self.text_edit.show()
        


    