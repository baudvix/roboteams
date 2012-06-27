import threading
from time import sleep

from mcc.model.robot import RobotNAO, RobotNXT
from mcc.control import command


class LogicCalibration(threading.Thread):
    """
    logical actions for calibration.
    wait for 1 nxt and 1 nao to connect
    tell the nao to locate the nxt
    onCalibration updating position and inform nxt
    """
    def __init__(self, robots):
        threading.Thread.__init__(self)
        self.robots = robots

    def run(self):
        sleep(1)
        has_nxt = False
        has_nao = False
        for robo in self.robots:
            if has_nxt and has_nao:
                break
            if type(robo) is type(RobotNXT):
                has_nxt = True
            if type(robo) is type(RobotNAO):
                has_nao = True

        if has_nxt and has_nao:
            for robo in self.robots:
                if type(robo) is type(RobotNAO):
                    nxt_robo = None
                    for obor in self.robots:
                        if type(obor) is type(RobotNXT):
                            nxt_robo = obor
                    robo.conncetion.callRemote(command.PerformCalibration, nxt_handle=nxt_robo.handle, color=nxt_robo.color)
