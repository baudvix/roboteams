from mcc.model import MapSection
from mcc.util import Point

class MapModel(object):

    def __init__(self):
        self.__firstMapSection = MapSection()
        self.__targetPosition = None

    def getFirstMapSection(self):
        return self.firstMapSection

    def getTargetPosition(self):
        return self.targetPosition

    def setFirstMapSection(self, mapSection):
        if mapSection is MapSection:
            self.firstMapSection = mapSection
        else:
            return False

    def setTargetPosition(self, targetPosition):
        if targetPosition is Point:
            self.targetPosition = targetPosition
        else:
            return False
