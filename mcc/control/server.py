"""
server provides the communication between the mcc and the robots
"""

from twisted.protocols import amp
from twisted.internet import reactor, task
from twisted.internet.protocol import Factory

from mcc.control import command
from mcc.model import robot
from mcc import utils


class MCCProtocol(amp.AMP):
    """
    MCCProtocol defines the reaction on incoming data and requests
    """
    def __init__(self):
        amp.AMP.__init__(self)
        #fixes for unresolved attribute
        self.factory = None

    def register(self, robot_type, color=None):
        """
        register defines the reaction on a new robot. the robot is added to
        the pool of robots and gets a unique handle
        """
        print 'NEW robot: type=%d color=%d' % (robot_type, color)
        if robot_type == robot.NXT_TYPE:
            self.factory.robots.append(robot.RobotNXT(self.factory.last_handle,
                                                      self, color))
        else:
            self.factory.robots.append(robot.RobotNAO(self.factory.last_handle,
                                                      self))
        self.factory.last_handle += 1
        return {'handle': (self.factory.last_handle - 1)}
    command.Register.responder(register)

    def activate(self, handle):
        """
        activate defines the reaction on a activation request it will issue an
        error if the handle doesn't exist. Else it will activate the robot in
        the pool of robots
        """
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo.active = True
                print '#%d activated' % handle
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
                #TODO: call thread with error calculation
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
                #TODO add calibrate NXT
                return {'ack': 'got spotted'}
        raise command.CommandNXTHandleError("No NXT robot with handle")
    command.NXTSpotted.responder(nxt_spotted)

    def send_data(self, handle, point_tag, x_axis, y_axis, yaw):
        """
        saves incoming data from the NXT
        """
        #TODO: save data in nxt (freespace, update position)
        print '#%d Send data %d: (%d, %d, %d)' % (handle, point_tag, x_axis,
                                                  y_axis, yaw)
        return{'ack': 'got data'}
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
        robo.point = utils.Point(x_axis, y_axis, yaw)
        if not to_nxt:
            return
        deffered = robo.connection.protocol.callRemote(command.UpdatePosition,
                                                        x_axis=x_axis,
                                                        y_axis=y_axis, yaw=yaw)
        deffered.addErrback(self.default_failure)

    def go_to_position(self, robo, x_axis, y_axis):
        deffered = robo.connection.protocol.callRemote(command.GoToPoint,
                                                        x_axis=x_axis,
                                                        y_axis=y_axis)
        deffered.addErrback(self.default_failure)

    def default_failure(self, error):
        print 'Error occurred', error


class MCCFactory(Factory):
    """
    MCCFactory provides variables for every protocol instance.
    Like the pool of robots and a counter of handles.
    """
    protocol = MCCProtocol

    def __init__(self):
        self.last_handle = 0
        self.robots = []
        #TODO: start a thread for heavy calculation
        #TODO: start a thread for view


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
        factory = MCCFactory()
        reactor.listenTCP(self.port, factory)

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


def main():
    """
    run this if the module is started as main
    """
    MCCServer()

if __name__ == '__main__':
    main()
