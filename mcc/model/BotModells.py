from time import gmtime

__author__ = 'mhhf'

class NXTModel(object):

    def __init__(self,positionPoint):
        self.typ = None
        self.lastCalibration
        self.position = positionPoint
        self.freeSpace = FreeSpace(positionPoint)
        self.trace = None

    def updatePosition(self,point,tag):
        self.freeSpace = self.FreeSpace(point,tag,self.freeSpace)


class Trace(object):

    def __init__(self,positionPoint):
        self.position = positionPoint
        self.next = None
        Trace.last = self

    def addNewPoint(self,positionPoint):
        newTrace = Trace(positionPoint)
        self.next = newTrace
        return  newTrace


class FreeSpace(object):

    def __init__(self,positionPoint,positionTag, parentPoint):
        self.time = gmtime()
        self.position = positionPoint
        self.pointTag = positionTag
        self.previousFreeSpace = parentPoint
