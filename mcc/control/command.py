from twisted.protocols import amp

#Commands from NXT or NAO to MCC

class Register(amp.Command):
    """
        Roboter registers itself at the Mission Control Center with his type and color
    """
    arguments = [('type', amp.Integer()), ('color', amp.Integer())]
    response = [('handle', amp.Integer()), ('port', amp.Integer()))]

#Commands from NAO to MCC

class NxtCalibrated(amp.Command):
    arguments = [('handle', amp.Integer()), ('nxthandle', amp.Integer()), ('x', amp.Integer()), ('y', amp.Integer()), ('yaw', amp.Integer())]
    response = [('ACK', amp.String())]

class NxtSpotted(amp.Command):
    arguments = [('handle', amp.Integer()), ('nxthandle', amp.Integer())]
    response = [('ACK', amp.String())]

#Commands from NXT to MCC

class SendData(amp.Command):
    arguments = [('handle', amp.Integer()), ('pointTag', amp.Integer()), ('x', amp.Integer()), ('y', amp.Integer()), ('yaw', amp.Float())]
    response = [('ACK', amp.String())]

class ArrivedPoint(amp.Command):
    arguments = [('handle', amp.Integer()), ('x', amp.Integer()), ('y', amp.Integer())]
    response = [('ACK', amp.String())]


#Commands from MCC to NXT or NAO

class UpdateState(amp.Command):
    arguments = [('state', amp.Integer())]
    response = [('ACK', amp.String())]

class UpdatePosition(amp.Command):
    arguments = [('x', amp.Integer()), ('y', amp.Integer()), ('yaw', amp.Integer())]
    response = [('ACK', amp.String())]

class SendMap(amp.Command):
    arguments = [('map', amp.AmpList([('value', amp.Integer()), ('type', amp.Integer())]))]
    response = [('ACK', amp.String())]

#Commands from MCC to NAO

class NxtMissing(amp.Command):
    arguments = [('nxthandle', amp.Integer())]
    response = [('ACK', amp.String())]

class PerformCalibration(amp.Command):
    arguments = [('nxthandle', amp.Integer())]
    response = [('ACK', amp.String())]

class SendPath(amp.Command):
    arguments = [('path', amp.AmpList([('x', amp.Integer()), ('y', amp.Integer())]))]
    response = [('ACK'), amp.String()]


#Commands from MCC to NXT

class GoToPoint(amp.Command):
    arguments = [('x', amp.Integer()), ('y', amp.Integer())]
    response = [('ACK', amp.String())]