from mcc.util import utils

class MapModel(object):

    def __init__(self):
        self.__firstMapSection = MapSection()
        self.__targetPosition = None

    @property
    def firstMapSection(self):
        return self.__firstMapSection

    @firstMapSection.setter
    def firstMapSection(self, mapSection):
        if not(type(mapSection) == type(MapSection())):
            print "Type \"mapSection\" excepted, but",  type(mapSection), " given."
            return

        self.__firstMapSection = mapSection

    @property
    def targetPosition(self):
        return self.__targetPosition

    @targetPosition.setter
    def targetPosition(self, targetPosition):
        if type(targetPosition) != type(utils.Point(0, 0)):
            print "Type \"Point\" excepted, but",  type(targetPosition), " given."
            return

        self.__targetPosition = targetPosition

    def addMapSection(self, offsetX, offsetY):
        if (type(offsetX) != type(1)) or (type(offsetY) != type(1)):
            print "Type \"int\" excepted, but", type(offsetX), ", ", type(offsetY), " given."
            return
        if offsetX == 0 and offsetY == 0:
            print "Can't add MapSection at position (0,0)."
            return

        tmpMapSection = self.__firstMapSection

        if offsetX > 0:
            for i in range(0, offsetX):
                tmpMapSection = tmpMapSection.rightGrid
        elif offsetX < 0:
            for i in range(0, offsetX, -1):
                tmpMapSection = tmpMapSection.leftGrid
        if offsetY > 0:
            for i in range(0, offsetY):
                tmpMapSection = tmpMapSection.topGrid
        elif offsetY < 0:
            for i in range(0, offsetY, -1):
                tmpMapSection = tmpMapSection.bottomGrid

        if (offsetX > 0 and tmpMapSection.rightGrid is not None) or\
           (offsetX < 0 and tmpMapSection.leftGrid is not None) or\
           (offsetY > 0 and tmpMapSection.topGrid is not None) or\
           (offsetY < 0 and tmpMapSection.bottomGrid is not None):
            print "Can't add MapSection with this offset - position is occupied."
            return



class MapSection(object):

    def __init__(self):
        self.__bottomGrid = None
        self.__leftGrid = None
        self.__topGrid = None
        self.__bottomGrid = None

        self.__GRID_HEIGHT = 10
        self.__GRID_WIDTH = 10

        self.__grid = []

        # initialize grid with zeros
        for i in range(0, self.__GRID_HEIGHT):
            self.__grid.append([])
            for j in range(0, self.__GRID_WIDTH):
                self.__grid[i].append(0)

    @property
    def bottomGrid(self):
        return self.__bottomGrid

    @bottomGrid.setter
    def bottomGrid(self, bottomGrid):
        if type(bottomGrid) != type(MapSection()):
            print "Type \"MapSection\" excepted, but",  type(bottomGrid), " given."
            return

        self.__bottomGrid = bottomGrid

    @property
    def leftGrid(self):
        return self.__leftGrid

    @leftGrid.setter
    def setLeftGrid(self, leftGrid):
        if type(leftGrid) != type(MapSection()):
            print "Type \"MapSection\" excepted, but",  type(leftGrid), " given."
            return

        self.__leftGrid = leftGrid

    @property
    def topGrid(self):
        return self.__topGrid

    @topGrid.setter
    def setTopGrid(self, topGrid):
        if type(topGrid) != type(MapSection()):
            print "Type \"MapSection\" excepted, but",  type(topGrid), " given."
            return

        self.__topGrid = topGrid

    @property
    def bottomGrid(self):
        return self.__bottomGrid

    @bottomGrid.setter
    def setBottomGrid(self, bottomGrid):
        if type(bottomGrid) != type(MapSection()):
            print "Type \"MapSection\" excepted, but",  type(bottomGrid), " given."
            return

        self.__bottomGrid = bottomGrid

    def updateGrid(self, points):
        if type(points) != type([]):
            print "Type \"List\" excepted, but",  type(points), " given."
            return

        for i in range (0, len(points)):
            if len(points[i]) != 2:
                print "Wrong format!"
                return

        for i in range (0, len(points)):
            self.__grid[points[i][0]][points[i][1]] += 1

    def printGrid(self):
        line = ""
        for i in range(0, self.__GRID_HEIGHT):
            for j in range(0, self.__GRID_WIDTH):
                line += str(self.__grid[i][j]) + "\t"
            print line
            line = ""
