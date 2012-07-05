
from twisted.internet import reactor

from mcc.control import server, command
from mcc.model import state, robot
from mcc.example import logic


class NaoWalkProtocol(server.MCCProtocol):

    def arrived_point(self, handle, x_axis, y_axis):
        """
        recognize and fire action
        """
        for robo in self.factory.robots:
            if robo.handle == handle:
                self.calc_action(x_axis, y_axis)
                print '#%d Arrived at (%d. %d)' % (handle, x_axis, y_axis)
                return {'ack': 'got arrival'}
        raise command.CommandHandleError("No robot with handle")

    def calc_action(self, x_axis, y_axis):
        if self.factory.state_machine.state == state.STATE_NAOWALK:
            x, y = self.factory.naowalk_logic.get_next_point(robot.NAO_TYPE)
            if x == None:
                raise command.CommandMissionCompletedError("Mission complete")
            else:
                robo = self.factory.naowalk_logic._robot_nao
                robo.connection.callRemote(command.GoToPoint,
                    handle=robo.handle, x_axis=x, y_axis=y)
        else:
            #TODO: Guided Exploration
            pass

    def nxt_followed(self, handle, nxt_handle, x_axis, y_axis):
        """
        move the nxt to the next position of the path
        """
        robo_exists = False
        for robo in self.factory.robots:
            if robo.handle == handle:
                robo_exists = True
        if not robo_exists:
            raise command.CommandHandleError("No nao with handle")
        for robo in self.factory.robots:
            if robo.handle == nxt_handle:
                x, y = self.factory.naowalk_logic.get_next_point(robo.robot_type)
                if x == None:
                    raise command.CommandMissionCompletedError("Mission complete")
                robo.connection.callRemote(command.GoToPoint,
                    handle=robo.handle, x_axis=x, y_axis=y)
                return {'ack': 'got followed'}
        raise command.CommandNXTHandleError("no nxt with handle")


class NaoWalkFactory(server.MCCFactory):

    protocol = NaoWalkProtocol

    def __init__(self, start_state=state.STATE_NAOWALK):
        server.MCCFactory.__init__(self)
        self.state_machine = state.StateMachine(start_state)
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
