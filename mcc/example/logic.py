#!/usr/bin/env python

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
                    defferd = robo.connection.callRemote(
                        command.PerformCalibration, nao_handle=robo.handle,
                        nxt_handle=nxt_robo.handle, color=nxt_robo.color)
                    print "Call for calib"
                    defferd.addCallback(self.print_out)
                    defferd.addErrback(self.failure)

    def print_out(self, response):
        print 'Success: NAO %d found NXT %d on (%d,%d)  with orientation %d' % (response['nao_handle'], response['nxt_handle'], response['x_axis'], response['y_axis'], response['yaw'])
        self.called_calibration = False

    def failure(self, error):
        print 'Error: %s' % (error)


class NaoWalk(object):

    #NXT stands on (0, 10) NAO on (0,0)
    def __init__(self, robots):
        self._path = [(0, 0), (0, 90), (60, 90), (80, 120)]
        self._status = -1
        self._robots = robots
        self._connected = False
        self._started = False
        self._robot_nxt = None
        self._robot_nao = None

    def run(self):
        if not self._connected:
            has_nxt = False
            has_nao = False
            self._robot_nxt = None
            self._robot_nao = None
            for robo in self._robots:
                if has_nxt and has_nao:
                    break
                if (robo.robot_type == robot.NXT_TYPE) and robo.active:
                    has_nxt = True
                    self._robot_nxt = robo
                if (robo.robot_type == robot.NAO_TYPE) and robo.active:
                    has_nao = True
                    self._robot_nao = robo
            if has_nao and has_nxt:
                self._connected = True
        if self._connected and not self._started:
            print "connected"
            #prepare list
            self._started = True
            plist = []
            for i in range(0, len(self._path)):
                plist.append({'x_axis': self._path[i][0],
                    'y_axis': self._path[i][1]})
            d_nao = self._robot_nao.connection.callRemote(command.SendPath,
                path=plist)
            d_nao.addCallback(self.print_out)
            d_nao.addErrback(self.failure)
            d_nxt = self._robot_nxt.connection.callRemote(
                command.UpdatePosition, x_axis=0, y_axis=10, yaw=0)
            d_nxt.addCallback(self.print_out)
            d_nxt.addErrback(self.failure)

    def print_out(self, ack):
        print 'Success: %s' % ack

    def failure(self, error):
        self._started = False
        print 'Error: %s' % error

    def get_next_point(self, robot_type):
        if robot_type == robot.NXT_TYPE:
            self._status += 1
        if self._status >= len(self._path):
            return (None, None)
        return self._path[self._status]
