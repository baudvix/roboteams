from mcc.model import robot
from mcc.control import command


class LogicCalibration():
    """
    logical actions for calibration.
    wait for 1 nxt and 1 nao to connect
    tell the nao to locate the nxt
    onCalibration updating position and inform nxt
    """
    def __init__(self):
        self.called_calibration = False

    def run(self, robots):
        if self.called_calibration:
            return
        has_nxt = False
        has_nao = False
        for robo in robots:
            if has_nxt and has_nao:
                break
            if robo.robot_type == robot.NXT_TYPE:
                print "got nxt"
                has_nxt = True
            if robo.robot_type == robot.NAO_TYPE:
                print "got nao"
                has_nao = True

        if has_nxt and has_nao:
            for robo in robots:
                if robo.robot_type == robot.NAO_TYPE:
                    nxt_robo = None
                    for robo2 in robots:
                        if robo2.robot_type == robot.NXT_TYPE:
                            nxt_robo = robo2
                    defferd = robo.connection.callRemote(command.PerformCalibration,
                        nxt_handle=nxt_robo.handle, color=nxt_robo.color)
                    print "Call for calib"
                    self.called_calibration = True

                    def print_out(ack):
                        print 'Success: %s' % ack

                    def failure(error):
                        print 'Error: %s' % (error)
                    defferd.addCallback(print_out)
                    defferd.addErrback(failure)
