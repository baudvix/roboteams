#!/usr/bin/env python
"""
server provides the communication between the mcc and the robots
"""
import time

from twisted.protocols import amp
from twisted.internet import reactor, task, defer
from twisted.internet import error as err
from twisted.internet.protocol import Factory

from mcc.control import command
from mcc.control.map_update import UpdateNXTData
from mcc.control.interpolate import Interpolate
from mcc.model import robot, map, state
from mcc.utils import Color, Point

from mcc.view import view
from mcc.example.logic import *

class MCCProtocol(amp.AMP):
    """
    MCCProtocol defines the reaction on incoming data and requests
    """
    def __init__(self):
        amp.AMP.__init__(self)
        self.factory = None

    def register(self, robot_type, rhandle, color=None):
        """
        register defines the reaction on a new robot. the robot is added to
        the pool of robots and gets a unique handle
        """
        print 'NEW robot: type=%d color=%d' % (robot_type, color)
        if robot_type == robot.NXT_TYPE:
            if not Color.is_color(color):
                raise command.CommandColorError('Unknown color. See utils.py@Color')
            self.factory.robots.append(robot.RobotNXT(self.factory.last_handle,
                                                      self, color))
        else:
            self.factory.robots.append(robot.RobotNAO(self.factory.last_handle, self))
        self.factory.last_handle += 1
        return {'rhandle': rhandle, 'handle': (self.factory.last_handle - 1)}
    command.Register.responder(register)

    def activate(self, handle):
        """
        activate defines the reaction on a activation request it will issue an
        error if the handle doesn't exist. Else it will activate the robot in
        the pool of robots
        """
        print "got activate %d " % handle
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo.active = True
                print '#%d activated' % handle
                self.update_position(robo, 0, 0, 0, True)
                return {'ack': 'got activate'}
        raise command.CommandHandleError('No robot with handle')
    command.Activate.responder(activate)

    def nxt_calibrated(self, handle, nxt_handle, x_axis, y_axis, yaw):
        """
        updates the current position of the calibrated NXT in the MCC and
        notifies the NXT about the new position
        """
        robo_handle = False
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo_handle = True
                break
        if not robo_handle:
            raise command.CommandHandleError("No robot with handle")
        for robo in self.factory.robots:
            if robo.handle == nxt_handle:
                self.update_position(robo, x_axis, y_axis, yaw, True)
                #NOTE TO SELF: use thread if this is a blocker
                robo.data = Interpolate(robo.data, [x_axis, y_axis])
                print '#%d NXT calibrated #%d (%d, %d, %d)' % (handle,
                                                               nxt_handle,
                                                               x_axis, y_axis,
                                                               yaw)
                return {'ack': 'got calibrated'}
        raise command.CommandNXTHandleError("No NXT robot with handle")
    command.NXTCalibrated.responder(nxt_calibrated)

    def nxt_spotted(self, handle, nxt_handle):
        """
        stops the NXT at his current position
        """
        robo_handle = False
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo_handle = True
                break
        if not robo_handle:
            raise command.CommandHandleError("No robot with handle")
        for robo in self.factory.robots:
            if robo.handle == nxt_handle:
                print '#%d Roboter spotted NXT #%d' % (handle, nxt_handle)
                self.go_to_position(robo, robo.x_axis, robo.y_axis)
                #TODO: calibrate nxt
                return {'ack': 'got spotted'}
        raise command.CommandNXTHandleError("No NXT robot with handle")
    command.NXTSpotted.responder(nxt_spotted)

    def nxt_followed(self, handle, nxt_handle, x_axis, y_axis):
        """
        move the nxt to the next position of the path
        """
        print "moving nxt to next point of the path"
        time.sleep(5)
        return {'ack': 'got followed'}
    command.NXTFollowed.responder(nxt_followed)

    def send_data(self, handle, point_tag, x_axis, y_axis, yaw):
        """
        saves incoming data from the NXT
        """
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo.put(Point(x_axis, y_axis, yaw), point_tag)
                #TODO: Respect dodges in update_map
                test = self.factory.tmp_update_map.insert_position_data(x_axis, y_axis, yaw)
                self.factory.maps[0].increase_points(test)
                print '#%d Send data %d: (%d, %d, %f)' % (handle, point_tag,
                                                          x_axis, y_axis, yaw)
                return{'ack': 'got data'}
        raise command.CommandHandleError("No NXT robot with handle")
    command.SendData.responder(send_data)

    def arrived_point(self, handle, x_axis, y_axis):
        """
        recognize and fire action
        """
        #TODO: calculate new go_to_position
        print '#%d Arrived at (%d. %d)' % (handle, x_axis, y_axis)
        return {'ack': 'got arrival'}
    command.ArrivedPoint.responder(arrived_point)

    def connectionLost(self, reason):
        """
        deactivates the robot if the connection is lost.
        """
        for robo in self.factory.robots:
            if robo.connection == self:
                robo.active = False
                print 'Connection Lost to robo %d ' % robo.handle

    def update_position(self, robo, x_axis, y_axis, yaw, to_nxt=False):
        robo.position = Point(x_axis, y_axis, yaw)
        if not to_nxt:
            return
        deffered = robo.connection.callRemote(command.UpdatePosition,
                                                        x_axis=x_axis,
                                                        y_axis=y_axis, yaw=yaw)
        deffered.addErrback(self.default_failure)

    def go_to_position(self, robo, x_axis, y_axis):
        deffered = robo.connection.callRemote(command.GoToPoint,
                                                        x_axis=x_axis,
                                                        y_axis=y_axis)
        deffered.addErrback(self.default_failure)

    def ball_lost(self, nao_handle, nxt_handle):
        print 'Ball lost'
        #do something, eg move nxt
        return {'ack': 'NXT moved'}
    command.BallLost.responder(ball_lost)

    def default_failure(self, error):
        if type(error) == err.ConnectionDone:
            print 'Error: Connection Done'
            #TODO: deactivate, wait for reactivation, ...
        print 'Error occurred', error

    def print_out(self, ack):
        print 'Success: %s' % ack


class MCCFactory(Factory):
    """
    MCCFactory provides variables for every protocol instance.
    Like the pool of robots and a counter of handles.
    """
    protocol = MCCProtocol

    def __init__(self, start_state):
        self.last_handle = 0
        self.state_machine = state.StateMachine(start_state)
        self.robots = []
        self.maps = []
        self.calibration = LogicCalibration()
        self.naowalk = NaoWalk()
        self.tmp_update_map = UpdateNXTData()
        self.maps.append(map.MapModel('Calibrated_Map'))
        #TODO: start a thread for heavy calculation
        #TODO: start a thread for view
        # self.initGUI()

    def initGUI(self):
        self._viewThread = view.View(self.maps[0])
        self._viewThread.daemon = True
        self._viewThread.start()


class MCCServer(object):
    """
    MCCServer provides the basic functionality of connecting and a loop called
    run for execute simple commands
    """

    def __init__(self):
        """
        initialises the server with some variables and let him listen on port
        5000
        """
        self.protocol = None
        self.factory = None
        self.host = 'localhost'
        self.port = 5000
        self.robots = None
        self.listen()
        loop = task.LoopingCall(self.run)
        loop.start(0.5)
        print 'MCC is started and listens on %d' % self.port
        reactor.run()

    def listen(self):
        """
        listen returns the deferred of the connector which was just created
        """
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        self.factory = MCCFactory(0)
        reactor.listenTCP(self.port, self.factory)

    def listening(self):
        """
        listening is called if the server was started successfully
        """

    def failure(self, error):
        """
        failure is called if the server wasn't started successfully
        """
        print 'Error: %s:%s\n%s' % (self.host, self.port, error)

    def run(self):
        """
        run is called in every loop of the reactor. so if you want to do
        something regularly you put it in here
        """
        #self.factory.calibration.run(self.factory.robots)
        self.factory.naowalk.run(self.factory.robots)



def main():
    """
    run this if the module is started as main
    """
    MCCServer()

if __name__ == '__main__':
    main()
