from mcc.model import robot
from mcc.control import command


class LogicCalibration():
    """
    logical actions for calibration.
    wait for 1 nxt and 1 nao to connect
    tell the nao to locate the nxt
    onCalibration updating position and inform nxt
    """
    def __init__(self, robots):
        self.called_calibration = False
        self.robots = robots

    def run(self):
        if self.called_calibration:
            return
        has_nxt = False
        has_nao = False
        for robo in self.robots:
            if has_nxt and has_nao:
                break
            if (robo.robot_type == robot.NXT_TYPE) and robo.active:
                has_nxt = True
            if (robo.robot_type == robot.NAO_TYPE) and robo.active:
                has_nao = True

        if has_nxt and has_nao:
            for robo in self.robots:
                if robo.robot_type == robot.NAO_TYPE:
                    nxt_robo = None
                    for robo2 in self.robots:
                        if robo2.robot_type == robot.NXT_TYPE:
                            nxt_robo = robo2
                    self.called_calibration = True
                    defferd = robo.connection.callRemote(command.PerformCalibration, nao_handle=robo.handle, nxt_handle=nxt_robo.handle, color=nxt_robo.color)
                    print "Call for calib"
                    defferd.addCallback(self.print_out)
                    defferd.addErrback(self.failure)

    def print_out(self, response):
        print 'Success: NAO %d found NXT %d on (%d,%d) with orientation %d' % (response['nao_handle'], response['nxt_handle'], response['x_axis'], response['y_axis'], response['yaw'])
        self.called_calibration = False

    def failure(self, error):
        print 'Error: %s' % (error)
