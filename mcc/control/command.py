#!/usr/bin/env python
"""
command holds all necessary commands for the communication between MCC, NAO
and NXT.
Those commands are based on amp the twisted Asynchronous Message Protocol.
"""

from twisted.protocols.amp import Command, Integer, String, AmpList, Float


class CommandTypeError(Exception):
    """
    Exception for an unknown robot type.
    """
    pass


class CommandHandleError(Exception):
    """
    Exception for an unknown handle
    The robot may register and activate first or activate again if the
    connection was lost.
    """
    pass


class CommandNXTHandleError(Exception):
    """
    Exception for a unknown handle of an NXT
    The NXT which the NAO spotted/ calibrated isn't activated or registered
    """
    pass


class CommandActiveError(Exception):
    """
    Exception for any robot who isn't activated, but has a correct handle.
    """
    pass


class CommandColorError(Exception):
    """
    Exception for a unknown color send by the NXT
    """
    pass


class CommandMissionCompleteError(Exception):
    """
    Well done mission completed. Lose connection please
    """
    pass


#Commands from NXT or NAO to MCC
class Register(Command):
    """
    The robot registers at the MCC with his type.
    NXT give their color with the request NAO send a -1.
    If the robot type doesn't exist an CommandTypeError is send back.
    """
    arguments = [('robot_type', Integer()),
                 ('color', Integer()),
                 ('rhandle', Integer())]
    response = [('rhandle', Integer()), ('handle', Integer())]
    error = [(CommandTypeError, 'COMMAND_TYPE_ERROR'),
             (CommandColorError, 'COMMAND_COLOR_ERROR')]


class Activate(Command):
    """
    The robot activates itself at the MCC.
    This is required at the beginning that the MCC knows it can send messages
    to the robot and if the connection was lost.
    If the handle doesn't exists an CommandHandleError is send back
    """
    arguments = [('handle', Integer())]
    response = [('ack', String())]
    error = [(CommandHandleError, 'COMMAND_HANDLE_ERROR')]


#Commands from NAO to MCC
class NXTCalibrated(Command):
    """
    The NAO sends to the MCC the data of the calibrated NXT
    If the handle doesn't exists an CommandHandleError is send back
    If the robot isn't activated an CommandActiveError is send back
    """
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer()),
                 ('yaw', Integer())]
    response = [('ack', String())]
    error = [(CommandHandleError, 'COMMAND_HANDLE_ERROR'),
             (CommandNXTHandleError, 'COMMAND_NXT_HANDLE_ERROR'),
             (CommandActiveError, 'COMMAND_ACTIVE_ERROR')]


class NXTSpotted(Command):
    """
    The NAO notifies the MCC about the spotted NXT, who was missing.
    If the handle doesn't exists an CommandHandleError is send back
    If the robot isn't activated an CommandActiveError is send back
    """
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer())]
    response = [('ack', String())]
    error = [(CommandHandleError, 'COMMAND_HANDLE_ERROR'),
             (CommandNXTHandleError, 'COMMAND_NXT_HANDLE_ERROR'),
             (CommandActiveError, 'COMMAND_ACTIVE_ERROR')]


class NXTFollowed(Command):
    """
    The NAO notifies the MCC about his arrival at the point of the path,
    where the NXT stands
    """
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer())]
    response = [('ack', String())]
    error = [(CommandMissionCompleteError, 'COMMAND_MISSION_COMPLETE_ERROR'),
             (CommandHandleError, 'COMMAND_HANDLE_ERROR'),
             (CommandNXTHandleError, 'COMMAND_NXT_HANDLE_ERROR')]


#Commands from NXT to MCC
class SendData(Command):
    """
    The NXT sends to the MCC his current position and the type
    If the handle doesn't exists an CommandHandleError is send back
    If the robot isn't activated an CommandActiveError is send back
    """
    arguments = [('handle', Integer()),
                 ('point_tag', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer()),
                 ('yaw', Float())]
    response = [('ack', String())]
    error = [(CommandHandleError, 'COMMAND_HANDLE_ERROR'),
             (CommandActiveError, 'COMMAND_ACTIVE_ERROR')]


class ArrivedPoint(Command):
    """
    The NXT notifies the MCC about is arrival at a given point
    If the handle doesn't exists an CommandHandleError is send back
    If the robot isn't activated an CommandActiveError is send back
    """
    arguments = [('handle', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer())]
    response = [('ack', String())]
    error = [(CommandMissionCompleteError, 'COMMAND_MISSION_COMPLETE_ERROR'),
             (CommandHandleError, 'COMMAND_HANDLE_ERROR'),
             (CommandActiveError, 'COMMAND_ACTIVE_ERROR')]


#Commands from MCC to NXT or NAO
class UpdateState(Command):
    """
    The MCC notifies the robot about the current mission state
    """
    arguments = [('handle', Integer()),
                 ('state', Integer())]
    response = [('ack', String())]


class UpdatePosition(Command):
    """
    The MCC notifies the robot about his current position
    """
    arguments = [('handle', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer()),
                 ('yaw', Integer())]
    response = [('ack', String())]


#TODO: this will never work. make a real type - module picke?
class SendMap(Command):
    """
    The MCC sends to the robot a copy of the current map
    """
    arguments = [('map', AmpList([('value', Integer()),
                                  ('type', Integer())]))]
    response = [('ack', String())]


#Commands from MCC to NAO
class NXTMissing(Command):
    """
    The MCC notifies the NAO about an missing NXT
    """
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer()),
                 ('color', Integer())]
    response = [('ack', String())]


class PerformCalibration(Command):
    """
    The MCC requests a calibration of a given NXT
    """
    arguments = [('handle', Integer()),
                 ('nxt_handle', Integer()),
                 ('color', Integer())]
    response = [('nao_handle', Integer()),
                ('nxt_handle', Integer()),
                ('x_axis', Integer()),
                ('y_axis', Integer()),
                ('yaw', Integer())]
    # errors = [(Exception, 'CALIBRATION_ERROR'),
    #          (NXTNotFoundException, 'NXT_NOT_FOUND')]


class SendPath(Command):
    """
    The MCC sends to the NAO the path to the target
    """
    arguments = [('handle', Integer()),
                 ('path', AmpList([('x_axis', Integer()),
                                   ('y_axis', Integer())]))]
    response = [('ack', String())]


#Commands from MCC to NXT
class GoToPoint(Command):
    """
    The MCC sends to the NXT a point to go to
    """
    arguments = [('handle', Integer()),
                 ('x_axis', Integer()),
                 ('y_axis', Integer())]
    response = [('ack', String())]

