import os

import obd

class Engine_Commands:
    def __init__(self):
        super().__init__()
        self.connection = obd.OBD(portstr=os.environ.get("OBD_PORT") or None)
        self.commands = obd.commands
    def query_obd(self, command):
        return self.connection.query(command).value
    def get_fuel_level(self):
        return self.query_obd(self.commands.FUEL_LEVEL)
    def get_engine_rpm(self):
        return self.query_obd(self.commands.RPM)
    def get_coolant_temp(self):
        return self.query_obd(self.commands.COOLANT_TEMP)
    def get_speed(self):
        return self.query_obd(self.commands.SPEED)
    def get_throttle_position(self):
        return self.query_obd(self.commands.THROTTLE_POS)
    def get_intake_air_temp(self):
        return self.query_obd(self.commands.INTAKE_TEMP)
    def get_intake_manifold_pressure(self):
        return self.query_obd(self.commands.INTAKE_PRESSURE)







