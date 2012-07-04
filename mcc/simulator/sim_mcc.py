
from mcc.control import server
from mcc.example.calibration import LogicCalibration


class CalibrationMCC(server.MCCServer):
    """
    Simulates a calibration which is triggerd by the mcc.
    """

    def __init__(self, arg):
        self.example_logic = LogicCalibration(self.factory.robots)
        server.MCCServer.__init__(self)

    def run(self):
        """
        run is called in every loop of the reactor. so if you want to do
        something regularly you put it in here
        """
        self.example_logic.run()
