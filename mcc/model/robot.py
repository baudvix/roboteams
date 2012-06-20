"""
robot provides a model of the robots and their functionality
"""
from time import gmtime
from mcc import utils
import Queue

NXT_TYPE = 0
NAO_TYPE = 1

#TODO make this module thread safe

class EmptyError(Exception):
    """
    This error is raised if the queue is empty
    """
    pass

class RobotBase():
    """
    the base class for NXT and NAO robots
    """
    def __init__(self, handle, connection):
        """
        initialise the queues and sets the handle and the connection
        """
        self.__in_queue = Queue.Queue()
        self.__out_queue = Queue.Queue()
        self.active = False
        self.handle = handle
        self.connection = connection
        self.point = None

    def get_point(self):
        """
        getter of point (property)
        """
        return self.point

    def set_point(self, point):
        """
        setter of point (property)
        """
        if type(point) is type(utils.Point):
            self.point = point
        else:
            raise TypeError("Use utils.Point")

    point = property(get_point, set_point)

    def put_out(self, *args, **kw):
        """
        add a command to the out_queue (thread safe)
        """
        self.__out_queue.put((args, kw), True)

    def get_out(self):
        """
        pop a command from the out_queue (thread safe)
        """
        if self.__out_queue.empty():
            raise EmptyError("Out-Queue is empty")
        else:
            return self.__out_queue.get(True)

    #TODO check for delete. if command is received, action should be called immediately
    def put_in(self, *args, **kw):
        """
        add a command to the in_queue (thread safe)
        """
        self.__in_queue.put((args, kw), True)

    def get_in(self):
        """
        pop a command from the in_queue (thread safe)
        """
        if self.__in_queue.empty():
            raise EmptyError("In-Queue is empty")
        else:
            return self.__in_queue.get(True)


class RobotNXT(RobotBase):
    """
    implements the RobotBase and some NXT specific functions
    i.e. the color
    """
    #TODO add Freespace and trace from NXTModel
    def __init__(self, handle, connection, color):
        RobotBase.__init__(self, handle, connection)
        self.color = color


class RobotNAO(RobotBase):
    """
    implements the RobotBase and some NAO specific functions
    """
    def __init__(self, handle, connection):
        RobotBase.__init__(self, connection, handle)

class NXTModel(object):
    """
        Model of an NXT
    """
    def __init__(self, position_point):
        """
            Constructor of the NXTModel
        """
        self.typ = None
        self.last_calibration = None
        self.position = position_point
        self.free_space = None
        self.trace = None

    def updatePosition(self, point, tag):
        """
            updatePosition adds a position of the NXT to the FreeSpace Stack
            :param point: Point of the NXT
            :type point: Point
            :param tag: Found Point tag of the Point
            :type tag: Enum
        """
        self.free_space = FreeSpace(point, tag, self.free_space)

class Trace(object):
    """
        The precessed NXT information as a Que
    """
    #TODO rewrite with Queue
    def __init__(self, position_point):
        """
            Constructor of the Trace Class
            :param positionPoint: Point of the NXT
            :type positionPoint: Point
        """
        self.position = position_point
        self.next = None
        Trace.last = self

    def addNewPoint(self, position_point):
        """
            adds a new Point to the Que
            :param positionPoint: point which is added to the Que
            :type x_coord: Point
        """
        new_trace = Trace(position_point)
        self.next = new_trace
        return  new_trace


class FreeSpace(object):
    """
        Model of the unprocessed data
    """
    #TODO rewrite with Queue
    def __init__(self, position_point, position_tag, parent_point):
        """
            Constructor of the FreeSpace class
            :param position_point: position of the Point
            :type position_point: Point
            :param position_tag: tag of the Point
            :type position_tag: Enum
            :param x_coord: link to the parrent FreeSpace in the Que
            :type x_coord: FreeSpace
        """
        self.time = gmtime()
        self.position = position_point
        self.pointTag = position_tag
        self.previousFreeSpace = parent_point
