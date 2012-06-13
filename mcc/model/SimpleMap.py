class SimpleMap(object):

    def __init__(self, nxtPosition, naoPosition):
        self.__nxtPosition = nxtPosition
        self.__naoPosition = naoPosition
        self.__firstMapSection = MapSection()
        self.__targetPosition = firstMapSection

    def getFirstMapSection(self):
        return self.firstMapSection