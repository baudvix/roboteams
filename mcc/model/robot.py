"""
robot provides a model of the robots and their functionality
"""
from mcc.model import map
from time import gmtime
import Queue

NXT_TYPE = 0
NAO_TYPE = 1

#TODO: make this module thread safe


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
        self.position = None

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

    #TODO: check for delete. if command is received, action should be called immediately
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
    def __init__(self, handle, connection, color):
        """
        Constructor for a new NXT
        """
        RobotBase.__init__(self, handle, connection)
        self.color = color
        self._trace = []
        self._data = []
        self.last_calibration = ''

    def put_data(self, position, data_type):
        """
        adds new data received by the NXT
        """
        self._data.append(DataNXT(position, data_type, DataNXT.DATA_NXT_NEW))
        if data_type == map.POINT_FREE or data_type == map.POINT_TARGET:
            self._trace.append(TraceNXT(position))

    def fget_data(self):
        """
        The data property getter.
        Use put_data to add a new TraceNXT and DataNXT element
        """
        return self._trace

    def fset_data(self, value):
        """The data property setter."""
        self._trace = value
    data = property(fget_data, fset_data)

    def fget_trace(self):
        """
        The trace property getter.
        Use put_data to add a new TraceNXT and DataNXT element
        """
        return self._trace

    def fset_trace(self, value):
        """The trace property setter."""
        self._trace = value
    trace = property(fget_trace, fset_trace)


class RobotNAO(RobotBase):
    """
    implements the RobotBase and some NAO specific functions
    """
    def __init__(self, handle, connection):
        """
        Constructor for a new NAO
        """
        RobotBase.__init__(self, connection, handle)


class TraceNXT(object):
    """
        The precessed NXT information as a Que
    """

    def __init__(self, position):
        """
        Constructor for a new Trace element
        """
        self._position = position
        self._time = gmtime()

    def fget_time(self):
        """The time property getter."""
        return self._time

    def fset_time(self, value):
        """The time property setter."""
        self._time = value
    time = property(fget_time, fset_time)

    def fget_position(self):
        """The position property getter."""
        return self._position

    def fset_position(self, value):
        """The position property setter."""
        self._position = value
    position = property(fget_position, fset_position)


class DataNXT(object):
    """
        Model of the unprocessed data
    """

    DATA_NXT_NEW = 0
    DATA_NXT_CURRENT = 1
    DATA_NXT_CALIBRATED = 2

    def __init__(self, position_point, position_tag, status):
        """
        Constructor for a new data element
        """
        self._time = gmtime()
        self._position = position_point
        self._type = position_tag
        self._status = status

    def fget_time(self):
        """The time property getter."""
        return self._time

    def fset_time(self, value):
        """The time property setter."""
        self._time = value
    time = property(fget_time, fset_time)

    def fget_position(self):
        """The position property getter."""
        return self._position

    def fset_position(self, value):
        """The position property setter."""
        self._position = value
    position = property(fget_position, fset_position)

    def fget_type(self):
        """The type property getter."""
        return self._type

    def fset_type(self, value):
        """The type property setter."""
        self._type = value
    type = property(fget_type, fset_type)

    def fget_status(self):
        """The status property getter."""
        return self._status

    def fset_status(self, value):
        """The status property setter."""
        self._status = value
    status = property(fget_status, fset_status)
