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

        #fuel label
        self.fuel_level = tk.Label(self.master, text="Fuel Level: ")
        self.fuel_level.grid(row=0, column=0)
        
        #rpm label
        self.engine_rpm = tk.Label(self.master, text="Engine RPM: ")
        self.engine_rpm.grid(row=1, column=0)
        
        #coolant temperature label
        self.coolant_temp = tk.Label(self.master, text="Coolant Temperature: ")
        self.coolant_temp.grid(row=2, column=0)
        
        #speed label    
        self.speed = tk.Label(self.master, text="Speed: ")
        self.speed.grid(row=3, column=0)

        #fuel data label
        self.fuel_level_data = tk.Label(self.master, text="0")
        self.fuel_level_data.grid(row=0, column=1)

        #rpm data label
        self.engine_rpm_data = tk.Label(self.master, text="0")
        self.engine_rpm_data.grid(row=1, column=1)
        
        #coolant temperature data label
        self.coolant_temp_data = tk.Label(self.master, text="0")
        self.coolant_temp_data.grid(row=2, column=1)
        
        #speed data label   
        self.speed_data = tk.Label(self.master, text="0")
        self.speed_data.grid(row=3, column=1)
        
        #add data for throttle position, intake air temperature, and intake manifold pressure
        self.throttle_position = tk.Label(self.master, text="Throttle Position: ")
        self.throttle_position.grid(row=4, column=0)

        self.intake_air_temp = tk.Label(self.master, text="Intake Air Temperature: ")
        self.intake_air_temp.grid(row=5, column=0)

        self.intake_manifold_pressure = tk.Label(self.master, text="Intake Manifold Pressure: ")
        self.intake_manifold_pressure.grid(row=6, column=0)

        self.throttle_position_data = tk.Label(self.master, text="0")
        self.throttle_position_data.grid(row=4, column=1)

        self.intake_air_temp_data = tk.Label(self.master, text="0")
        self.intake_air_temp_data.grid(row=5, column=1)

        self.intake_manifold_pressure_data = tk.Label(self.master, text="0")
        self.intake_manifold_pressure_data.grid(row=6, column=1)
        
        #add data for fuel pressure, barometric pressure, and timing advance
        

#update the data automatically
    def update_data(self):
        self.fuel_level_data.config(text=commands.get_fuel_level())
        self.engine_rpm_data.config(text=commands.get_engine_rpm())
        self.coolant_temp_data.config(text=commands.get_coolant_temp())
        self.speed_data.config(text=commands.get_speed())
        self.throttle_position_data.config(text=commands.get_throttle_position())
        self.intake_air_temp_data.config(text=commands.get_intake_air_temp())
        self.intake_manifold_pressure_data.config(text=commands.get_intake_manifold_pressure())
        self.master.after(1000, self.update_data)
        
