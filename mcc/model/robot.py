from time import gmtime
import Queue

class EmptyError(Exception):
    pass

class RoboterBase():

    def __init__(self, handle):
        self.__in_queue = Queue.Queue()
        self.__out_queue = Queue.Queue()
        self.__active = False
        self.__handle = handle
        self.__connection = None

    def is_active(self):
        return self.__active

    def set_active(self, active):
        self.__active = active

    active = property(is_active, set_active)


    def get_connection(self):
        return self.__connection

    def set_connection(self, connection):
        self.__connection = connection

    deffer = property(get_connection, set_connection)

    def get_handle(self):
        return self.__handle

    def set_handle(self, handle):
        self.__handle = handle

    handle = property(get_handle, set_handle)

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
        self.free_space = FreeSpace(position_point)
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

    def updateTrace(self,point):

        self.trace = self.trace.addNewPoint(point)


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
