import obd

class Engine_Commands:
    #Constructor
    def __init__(self):
        self.connection = obd.OBD(portstr="COM7")
        self.commands = obd.commands

        #Get the fuel level
    def get_fuel_level(self):
        return self.connection.query(self.commands.FUEL_LEVEL).value

        #Get the engine RPM
    def get_engine_rpm(self):
        return self.connection.query(self.commands.RPM).value

        #Get the coolant temperature
    def get_coolant_temp(self):
        return self.connection.query(self.commands.COOLANT_TEMP).value

        #Get the vehicle speed
    def get_speed(self):
        return self.connection.query(self.commands.SPEED).value
    
        #Get the throttle position
    def get_throttle_position(self):
        return self.connection.query(self.commands.THROTTLE_POS).value

        #Get the intake air temperature
    def get_intake_air_temp(self):
        return self.connection.query(self.commands.INTAKE_TEMP).value

        #Get the intake manifold pressure
    def get_intake_manifold_pressure(self):
        return self.connection.query(self.commands.INTAKE_PRESSURE).value


        
    


