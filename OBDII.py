import obd
from time import sleep
from Main_Window import Main_Window
import tkinter as tk
from Engine_Commands import Engine_Commands

if __name__ == "__main__":
    #create an instance of the tkinter module
    root = tk.Tk()
#instantiate the Main_Window class
    app = Main_Window(root)
#run the update_data method
    root.after(0, app.update_data())
#run the tkinter module
    root.mainloop()
   



    


