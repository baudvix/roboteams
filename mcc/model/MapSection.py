class MapSection(object):

    def __init__(self):
        self.__rightGrid = None
        self.__leftGrid = None
        self.__topGrid = None
        self.__bottomGrid = None

        self.__GRID_HEIGHT = 100
        self.__GRID_WIDTH = 100

        self.__grid = []

        # initialize grid with zeros
        for i in range(0, self.__GRID_HEIGHT):
            self.__grid.append([])
            for j in range(0, self.__GRID_WIDTH):
                self.__grid[i].append(0)


    def setRightGrid(self, rightGrid):
        if rightGrid in MapSection:
            self.__rightGrid = rightGrid
        else:
            return False

    def setLeftGrid(self, leftGrid):
        if leftGrid in MapSection:
            self.__leftGrid = leftGrid
        else:
            return False

    def setTopGrid(self, topGrid):
        if topGrid in MapSection:
            self.__topGrid = topGrid
        else:
            return False

    def setBottomGrid(self, bottomGrid):
        if bottomGrid in MapSection:
            self.__bottomGrid = bottomGrid
        else:
            return False

    def getRightGrid(self):
        return self.__rightGrid

    def getLeftGrid(self):
        return self.__leftGrid

    def getTopGrid(self):
        return self.__topGrid

    def getBottomGrid(self):
        return self.__bottomGrid

    def updateGrid(self):
        pass

    def printGrid(self):
        line = ""
        for i in range(0, 10):
            for j in range(0, 10):
                line += str(self.__grid[i][j]) + "\t"

            print line
            line = ""
