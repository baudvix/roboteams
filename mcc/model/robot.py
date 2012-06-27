from time import gmtime
import Queue

NXT_TYPE = 0
NAO_TYPE = 1

NAO_COLOR = -1

class EmptyError(Exception):
    pass

class RobotBase():

    def __init__(self, handle, connection):
        self.__in_queue = Queue.Queue()
        self.__out_queue = Queue.Queue()
        self.active = False
        self.handle = handle
        self.connection = connection

    def put_out(self, *args, **kw):
        self.__out_queue.put((args, kw), True)

    def get_out(self):
        if self.__out_queue.empty():
            raise EmptyError("Out-Queue is empty")
        else:
            return self.__out_queue.get(True)

    def put_in(self, *args, **kw):
        self.__out_queue.put((args, kw), True)

    def get_in(self):
        if self.__in_queue.empty():
            raise EmptyError("In-Queue is empty")
        else:
            return self.__out_queue.get(True)


class RobotNXT(RobotBase):

    def __init__(self, handle, connection, color):
        RobotBase.__init__(self, handle, connection)
        self.color = color


class RobotNAO(RobotBase):

    def __init__(self, handle, connection):
        RobotBase.__init__(self, handle,  connection)

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
