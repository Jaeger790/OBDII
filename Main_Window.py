import tkinter as tk
import asyncio
from Engine_Commands import Engine_Commands
import obd

class Main_Window:
    #Constructor



    def __init__(self, master):
        self.master = master
        self.master.title("OBDII")
        self.master.geometry("1000x1000")
        self.master.resizable(False, False)
        self.commands = Engine_Commands()


        

        #fuel label
        self.fuel_level = tk.Label(self.master, text="Fuel Level: ")
        self.fuel_level.grid(row=0, column=0)
        
        #fuel data label
        self.fuel_level_data = tk.Label(self.master, text="0")
        self.fuel_level_data.grid(row=0, column=1)
        
        #rpm label
        self.engine_rpm = tk.Label(self.master, text="Engine RPM: ")
        self.engine_rpm.grid(row=1, column=0)

        #rpm data label
        self.engine_rpm_data = tk.Label(self.master, text="0")
        self.engine_rpm_data.grid(row=1, column=1)
        
        #coolant temperature label
        self.coolant_temp = tk.Label(self.master, text="Coolant Temperature: ")
        self.coolant_temp.grid(row=2, column=0)

        #coolant temperature data label
        self.coolant_temp_data = tk.Label(self.master, text="0")
        self.coolant_temp_data.grid(row=2, column=1)
        
        #speed label    
        self.speed = tk.Label(self.master, text="Speed: ")
        self.speed.grid(row=3, column=0)

        #speed data label   
        self.speed_data = tk.Label(self.master, text="0")
        self.speed_data.grid(row=3, column=1)
        
        #throttle position label
        self.throttle_position = tk.Label(self.master, text="Throttle Position: ")
        self.throttle_position.grid(row=4, column=0)

        #throttle position data label
        self.throttle_position_data = tk.Label(self.master, text="0")
        self.throttle_position_data.grid(row=4, column=1)
        
        #intake air temperature label
        self.intake_air_temp = tk.Label(self.master, text="Intake Air Temperature: ")
        self.intake_air_temp.grid(row=5, column=0)
        
        #intake air temperature data label
        self.intake_air_temp_data = tk.Label(self.master, text="0")
        self.intake_air_temp_data.grid(row=5, column=1)

        #intake manifold pressure label
        self.intake_manifold_pressure = tk.Label(self.master, text="Intake Manifold Pressure: ")
        self.intake_manifold_pressure.grid(row=6, column=0)

        #intake manifold pressure data label
        self.intake_manifold_pressure_data = tk.Label(self.master, text="0")
        self.intake_manifold_pressure_data.grid(row=6, column=1)
        
        #TODO: add data for fuel pressure, barometric pressure, and timing advance
#create a background container to display the speedometer
        
        
        #create a speedometer using a canvas
        self.canvas = tk.Canvas(self.master, width=800, height=800, background="gray")
        self.canvas.grid(row=7, column=5, columnspan=4)
        #center the oval in the canvas
        self.canvas.create_oval(50, 50, 300, 300, fill="black")
        #create the speedometer needle
        self.canvas.create_line(175, 175, 175, 50, fill="red", width=3)
        #create the speedometer needle center
        self.canvas.create_oval(170, 170, 180, 180, fill="red")       
        #create the speedometer needle tip
        self.canvas.create_oval(170, 50, 180, 60, fill="red")               
        #create the speedometer labels
        self.canvas.create_text(175, 25, text="0")
        self.canvas.create_text(250, 50, text="20")
        self.canvas.create_text(300, 100, text="40")
        self.canvas.create_text(325, 175, text="60")
        self.canvas.create_text(300, 250, text="80")
        self.canvas.create_text(250, 300, text="100")
        
    #create the rpm gauge
        self.canvas.create_oval(500, 50, 750, 300, fill="black")
        #create the rpm needle
        needle =  self.canvas.create_line(625, 175, 625, 50, fill="red", width=3)
        #create the rpm needle center
        self.canvas.create_oval(620, 170, 630, 180, fill="red")
        #create the rpm needle tip
        self.canvas.create_oval(620, 50, 630, 60, fill="red")
        #create the rpm labels
        self.canvas.create_text(625, 25, text="0")
        self.canvas.create_text(700, 50, text="500")
        self.canvas.create_text(750, 100, text="1000")
        self.canvas.create_text(775, 175, text="1500")
        self.canvas.create_text(750, 250, text="2000")
        self.canvas.create_text(700, 300, text="3000")
        self.canvas.create_text(625, 325, text="3300")
        self.canvas.create_text(550, 300, text="4000")
        self.canvas.create_text(500, 250, text="5000") 
        self.canvas.create_text(475, 175, text="5500")
        self.canvas.create_text(500, 100, text="6000")
        self.canvas.create_text(550, 50, text="7000")
        







      


    #update the user interface with the data from the car
    def update_data(self):
        self.fuel_level_data.config(text=self.commands.get_fuel_level())
        self.engine_rpm_data.config(text=self.commands.get_engine_rpm())
        self.coolant_temp_data.config(text=self.commands.get_coolant_temp())
        self.speed_data.config(text=self.commands.get_speed())
        self.throttle_position_data.config(text=self.commands.get_throttle_position())
        self.intake_air_temp_data.config(text=self.commands.get_intake_air_temp())
        self.intake_manifold_pressure_data.config(text=self.commands.get_intake_manifold_pressure())
        self.master.after(300, self.update_data)
        
