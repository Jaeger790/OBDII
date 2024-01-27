import asyncio
import obd

class Engine_Commands:
    #create a constructor
    def __init__(self):
        self.connection = obd.Async()
        self.connection.watch(obd.commands.FUEL_LEVEL)
        self.connection.watch(obd.commands.RPM)
        self.connection.watch(obd.commands.COOLANT_TEMP)
        self.connection.watch(obd.commands.SPEED)
        self.connection.start()
        self.connection.stop()
    
    #create an async connection to get the fuel level in percentage
    def get_fuel_level(self):
        self.connection.watch(obd.commands.FUEL_LEVEL)
        self.connection.start()

        response = self.connection.query(obd.commands.FUEL_LEVEL).value
        self.connection.stop()
        return response
    
#create an async connection to get the engine RPM
    def get_engine_rpm(self):
        self.connection.watch(obd.commands.RPM)
        self.connection.start()
    

        response = self.connection.query(obd.commands.RPM).value
        self.connection.stop()
        return response
        
    
#create an async connection to get the coolant temperature
    def get_coolant_temp(self):
        self.connection.watch(obd.commands.COOLANT_TEMP)
        self.connection.start()
    

        response = self.connection.query(obd.commands.COOLANT_TEMP).value
        self.connection.stop()
        return response
    
#create an async connection to get the speed
    def get_speed(self):
        self.connection.watch(obd.commands.SPEED)
        self.connection.start()
    

        response = self.connection.query(obd.commands.SPEED).value
        self.connection.stop()
        return response
        
    


