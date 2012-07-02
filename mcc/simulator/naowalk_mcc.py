
from twisted.internet import reactor

from mcc.control import server, command
from mcc.model import state
from mcc.example import logic


class NaoWalkProtocol(server.MCCProtocol):

    def arrived_point(self, handle, x_axis, y_axis):
        """
        recognize and fire action
        """
        for robo in self.factory.robots:
            if robo.handle == handle:
                self.calc_action(robo, x_axis, y_axis)
                print '#%d Arrived at (%d. %d)' % (handle, x_axis, y_axis)
                return {'ack': 'got arrival'}
        raise command.CommandHandleError("No robot with handle")

    def calc_action(self, robo, x_axis, y_axis):
        x, y = self.factory.naowalk_logic.get_next_point(robo.robot_type)
        if x == None:
            print "mission complete"
        else:
            robo.connection.callRemote(command.GoToPoint, x_axis=x, y_axis=y)


class NaoWalkFactory(server.MCCFactory):

    protocol = NaoWalkProtocol

    def __init__(self, start_state=0):
        server.MCCFactory.__init__(self, start_state)
        self.naowalk_logic = logic.NaoWalk(self.robots)

    def initGUI(self):
        pass


class NaoWalkMCC(server.MCCServer):
    """
    Simulates a calibration which is triggerd by the mcc.
    """

    def __init__(self):
        server.MCCServer.__init__(self)

    def run(self):
        """
        run is called in every loop of the reactor. so if you want to do
        something regularly you put it in here
        """
        self.factory.naowalk_logic.run()

    def listen(self):
        """
        listen returns the deferred of the connector which was just created
        """
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        self.factory = NaoWalkFactory(state.STATE_NAOWALK)
        reactor.listenTCP(self.port, self.factory)

if __name__ == '__main__':
    NaoWalkMCC()
