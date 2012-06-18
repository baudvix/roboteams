from twisted.protocols.amp import Command, Integer, String, AmpList, Float


#Commands from NXT or NAO to MCC
class Register(Command):
    """
    Roboter registers itself at the Mission Control Center with his type and color
    """
    arguments = [('type', Integer()),
                 ('color', Integer())]
    response = [('handle', Integer())]


class Activate(Command):
    """
    Roboter activates itself at the Mission Control Center.
    """
    arguments = [('handle', Integer())]
    response = [('ACK', String())]


#Commands from NAO to MCC
class NXTCalibrated(Command):
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer()),
                 ('x', Integer()),
                 ('y', Integer()),
                 ('yaw', Integer())]
    response = [('ACK', String())]


class NXTSpotted(Command):
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer())]
    response = [('ACK', String())]


#Commands from NXT to MCC
class SendData(Command):
    arguments = [('handle', Integer()),
                 ('pointTag', Integer()),
                 ('x', Integer()),
                 ('y', Integer()),
                 ('yaw', Float())]
    response = [('ACK', String())]


class ArrivedPoint(Command):
    arguments = [('handle', Integer()),
                 ('x', Integer()),
                 ('y', Integer())]
    response = [('ACK', String())]


#Commands from MCC to NXT or NAO
class UpdateState(Command):
    arguments = [('state', Integer())]
    response = [('ACK', String())]


class UpdatePosition(Command):
    arguments = [('x', Integer()),
                 ('y', Integer()),
                 ('yaw', Integer())]
    response = [('ACK', String())]


class SendMap(Command):
    arguments = [('map', AmpList([('value', Integer()),
                                  ('type', Integer())]))]
    response = [('ACK', String())]


#Commands from MCC to NAO
class NXTMissing(Command):
    arguments = [('nxt_handle', Integer()),
                 ('color', Integer())]
    response = [('ACK', String())]


class PerformCalibration(Command):
    arguments = [('nxt_handle', Integer()),
                 ('color', Integer())]
    response = [('ACK', String())]


class SendPath(Command):
    arguments = [('path', AmpList([('x', Integer()),
                                   ('y', Integer())]))]
    response = [('ACK'), String()]


#Commands from MCC to NXT
class GoToPoint(Command):
    arguments = [('x', Integer()),
                 ('y', Integer())]
    response = [('ACK', String())]