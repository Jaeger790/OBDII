
import obd

class Engine_Commands:
    #create a constructor
    def __init__(self):
        #create a connection to the car using the obd module
        self.connection = obd.OBD(portstr="COM7")
        #instantiate the commands class from the obd module
        self.commands = obd.commands


        #create a function that will return the fuel level
    def get_fuel_level(self):
        response = self.connection.query(self.commands.FUEL_LEVEL)
        return response

        #create a function that will return the engine rpm
    def get_engine_rpm(self):
        response = self.connection.query(self.commands.RPM)
        return response

        #create a function that will return the coolant temperature
    def get_coolant_temp(self):
        response = self.connection.query(self.commands.COOLANT_TEMP)
        return response

        #create a function that will return the speed
    def get_speed(self):
        response = self.connection.query(self.commands.SPEED)
        return response
    
        

        #create a function that will return the throttle position
    def get_throttle_position(self):
        #return the throttle position
        response = self.connection.query(self.commands.THROTTLE_POS)
        return response

            

        #create a function that will return the intake air temperature
    def get_intake_air_temp(self):
        #return the intake air temperature

        return self.connection.query(self.commands.INTAKE_TEMP)

    #create a function that will return the intake manifold pressure
    def get_intake_manifold_pressure(self):
        #return the intake manifold pressure
        return self.connection.query(self.commands.INTAKE_PRESSURE)


        
    


