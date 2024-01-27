import obd
from obd import commands
from Main_Window import Main_Window
import tkinter as tk
from Engine_Commands import Engine_Commands

if __name__ == "__main__":
#instantiate the tkinter module
    root = tk.Tk()
    #instantiate the Main_Window class
    main_window = Main_Window(root)
    #instantiate the Engine_Commands class
    commands = Engine_Commands()
    #run the update_data method from the Main_Window class
    main_window.update_data()
    #run the tkinter module
    root.mainloop()

   



    


