#import the tkinter module
import tkinter as tk
import asyncio
#import the Engine_Commands class from Engine_Commands.py
from Engine_Commands import Engine_Commands
#import the obd module
import obd
#instantiate the Engine_Commands class
commands = Engine_Commands()



#create a user interface that will display the data from the car
class Main_Window:
    def __init__(self, master):
        self.master = master
        self.master.title("OBDII")
        self.master.geometry("500x500")
        self.master.resizable(False, False)

        self.fuel_level = tk.Label(self.master, text="Fuel Level: ")
        self.fuel_level.grid(row=0, column=0)

        self.engine_rpm = tk.Label(self.master, text="Engine RPM: ")
        self.engine_rpm.grid(row=1, column=0)

        self.coolant_temp = tk.Label(self.master, text="Coolant Temperature: ")
        self.coolant_temp.grid(row=2, column=0)

        self.speed = tk.Label(self.master, text="Speed: ")
    
        self.speed.grid(row=3, column=0)

        self.fuel_level_data = tk.Label(self.master, text="0")
        self.fuel_level_data.grid(row=0, column=1)

        self.engine_rpm_data = tk.Label(self.master, text="0")
        self.engine_rpm_data.grid(row=1, column=1)

        self.coolant_temp_data = tk.Label(self.master, text="0")
        self.coolant_temp_data.grid(row=2, column=1)

        self.speed_data = tk.Label(self.master, text="0")
        self.speed_data.grid(row=3, column=1)
        

#update the data automatically
    def update_data(self):
        #await each command to finish

            #update the data
        self.fuel_level_data.config(text=commands.get_fuel_level())
        self.engine_rpm_data.config(text=commands.get_engine_rpm())
        self.coolant_temp_data.config(text=commands.get_coolant_temp())
        self.speed_data.config(text=commands.get_speed())
            #run the update_data method again after 1 second
        self.master.after(1000, self.update_data)


            




