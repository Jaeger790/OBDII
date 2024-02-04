import sys
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout,QHeaderView, QTableWidget, QTableView,QTableWidgetItem, QApplication, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
class DTC_Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DTC Window")
        self.setGeometry(600, 600, 800, 1200)
        self.setStyleSheet("background-color: rgba(65, 105, 225,.4);")
        
        self.layout = QGridLayout()
        self.setLayout(self.layout) 

        #Create table for Reading DTC Codes
        self.table = QTableView(self)
        self.model = QStandardItemModel(self)

        #TODO: Add data from scanner to the table.
        data = ["DTC Code", "Description"]

        #Todo: Display the data gathered from the scanner
        #insert data into the table using the required QStandardItem
        items = [QStandardItem(text) for text in data]
        self.model.appendRow(items)

        # set header properties
        headers = ["DTC Code", "Description"]
        self.model.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section{
                color: black; 
                background-color: rgba(150,0,255,255);
                border: 2px solid black; 
                font-size: 24px; 
                font-family: Fira Code; 
                font-weight: bold; 
            }""") 
        self.table.verticalHeader().setStyleSheet("""
            QHeaderView::section{
                color: black;
                background-color: rgba(150,0,255,255);
                border: 2px solid black;
                font-size: 24px;
                font-family: Fira Code;
                font-weight: bold;
            }""")
        
        self.table.setModel(self.model)

        
        self.table.setFixedSize(800, 800)
        self.table.setStyleSheet("""
            QTableView::item{
                color: white;
                background-color: rgba(0,0,255,255);
                font-size: 22px;
                font-family: Fira Code;
            }
            QTableView::corner{
                color:rgba(150,0,255,255);
                background-color: rgba(150,0,255,255);
            }
                                 
            """)
        
        # Add shadow effect to the table
        table_shadow = QGraphicsDropShadowEffect(self.table)
        table_shadow.setBlurRadius(10)
        table_shadow.setXOffset(3)
        table_shadow.setYOffset(3)
        table_shadow.setColor(QColor(0, 0, 0, 255))
        self.table.setGraphicsEffect(table_shadow)


        #set column width
        self.table.setColumnWidth(0, 150)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)

        self.layout.addWidget(self.table, 0, 0)




        #Window Title label
        self.page_title = QLabel(self)
        self.page_title.setText("DTC Code Reader")
        self.page_title.setFixedSize(400, 50)
        self.page_title.setStyleSheet("""
            color: black; background-color: rgba(150,0,255);
            border: 2px solid black; font-size: 24px; font-weight: bold;
            font-family: Fira Code;
            """)

        
        
        self.show()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DTC_Window()
    window.show()
    sys.exit(app.exec_())   
