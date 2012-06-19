

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
            :param position_point: Point of the NXT
            :type position_point: Point
        """
        self.position = position_point
        self.next = None
        Trace.last = self

    def addNewPoint(self, position_point):
        """
            adds a new Point to the Que
            :param position_point: point which is added to the Que
            :type position_point: Point
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

        """
        self.time = gmtime()
        self.position = position_point
        self.pointTag = position_tag
        self.previousFreeSpace = parent_point
