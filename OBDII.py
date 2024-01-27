import obd
from obd import commands
from Main_Window import Main_Window
import tkinter as tk
from Engine_Commands import Engine_Commands

if __name__ == "__main__":
    root = tk.Tk()
    main_window = Main_Window(root)
    commands = Engine_Commands()
    main_window.update_data()
    root.mainloop()

   



    


