"""
Module for the map model

"""

from mcc import utils

class MapModel:
    """
    Class for the MapModel. Contains the reference to the first map section
    which contains the position of the NAO.

    """

    def __init__(self):
        """
        Creates a map model

        :return: 'MapModel' with an initial map section ('first_map_section')
                 and a target position ('target_position')
        :rtype: MapModel

        """
        self.__first_map_section = MapSection()
        self.__target_position = None

    @property
    def first_map_section(self):
        """
        Getter method for first_map_section

        :return: first map section in the map model
        :rtype: MapSection
        
        """
        return self.__first_map_section

    @first_map_section.setter
    def first_map_section(self, map_section):
        """
        Setter method for first_map_section

        :param map_section: map section to replace the current
        :type map_section: MapSection
        :raises TypeError: If the type of the arguments is not MapSection
        
        """
        if type(map_section) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted,\
                             but",  type(map_section), " given.")

        self.__first_map_section = map_section

    @property
    def target_position(self):
        """
        Getter method for target_position

        :return: position of the target in the map model
        :rtype: Point
        
        """
        return self.target_position

    @target_position.setter
    def target_position(self, target_position):
        """
        Setter method for target_position

        :param target_position: point to replace the current target position
        :type target_position: Point
        :raises TypeError: If the type of the arguments is not Point
        
        """
        if type(target_position) != type(utils.Point(0, 0)):
            raise TypeError("Type \"Point\" excepted, but",
                            type(target_position), " given.")

        self.__target_position = target_position

    def add_map_section(self, offset_x, offset_y):
        """
        Adds a map section at the position stated with the offset.
        If there are free spaces (no grids) in the way to the position,
        where the new grid will be placed, they are automatically created.

        :param offset_x: identifies the steps on the x-axis
        :type offset_x: int
        :param offset_y: identifies the steps on the y-axis
        :type offset_y: int
        :raises TypeError: If the type of the arguments is not integer
        :raises ValueError: If the offset is (0,0) or already occupied
        
        """
        if (type(offset_x) != type(1)) or (type(offset_y) != type(1)):
            raise TypeError("Type \"int\" excepted, but", type(offset_x),
                            ", ", type(offset_y), " given.")
        if offset_x == 0 and offset_y == 0:
            raise ValueError("Can't add MapSection at position (0,0).")

        tmp_map_section = self.__first_map_section

        if offset_x > 0:
            for i in range(0, offset_x):
                if tmp_map_section.right_grid is None:
                    tmp_map_section.right_grid = MapSection()
                tmp_map_section = tmp_map_section.right_grid
        elif offset_x < 0:
            for i in range(0, offset_x, -1):
                if tmp_map_section.left_grid is None:
                    tmp_map_section.left_grid = MapSection()
                tmp_map_section = tmp_map_section.left_grid
        if offset_y > 0:
            for i in range(0, offset_y):
                if tmp_map_section.top_grid is None:
                    tmp_map_section.top_grid = MapSection()
                tmp_map_section = tmp_map_section.top_grid
        elif offset_y < 0:
            for i in range(0, offset_y, -1):
                if tmp_map_section.bottom_grid is None:
                    tmp_map_section.bottom_grid = MapSection()
                tmp_map_section = tmp_map_section.bottom_grid

        if (offset_x > 0 and tmp_map_section.right_grid is not None) or\
           (offset_x < 0 and tmp_map_section.left_grid is not None) or\
           (offset_y > 0 and tmp_map_section.top_grid is not None) or\
           (offset_y < 0 and tmp_map_section.bottom_grid is not None):
            raise ValueError("Can't add MapSection with this offset - \
                             position is occupied.")


class MapSection(object):
    """
    Class for the MapSection. Contains the references to the bordering grids
    and the grid which is defined by 'GRID_HEIGHT' and 'GRID_WIDTH'.

    """
    def __init__(self):
        """
        Creates a map section

        :return: 'MapSection' right -, left-, top- and bottom-grid
                 which are initially all None
        :rtype: MapSection
        
        """
        self.__right_grid = None
        self.__left_grid = None
        self.__top_grid = None
        self.__bottom_grid = None

        self.__GRID_HEIGHT = 10
        self.__GRID_WIDTH = 10

        self.__grid = []

        # initialize grid with zeros
        for i in range(0, self.__GRID_HEIGHT):
            self.__grid.append([])
            for j in range(0, self.__GRID_WIDTH):
                self.__grid[i].append(0)

    @property
    def right_grid(self):
        """
        Getter method for right_grid
    
        :return: the grid which is concatenated at the right of this grid
        :rtype: MapSection
        
        """ 
        return self.__bottom_grid

    @right_grid.setter
    def right_grid(self, right_grid):
        """
        Setter method for right_grid

        :param right_grid: grid to replace the reference to the current 
                           right grid 
        :type right_grid: MapSection
        :raises TypeError: If the type of the arguments is not MapSection
        
        """
        if type(right_grid) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted, but",
                            type(right_grid), " given.")

        self.__right_grid = right_grid

    @property
    def left_grid(self):
        """
        Getter method for left_grid
    
        :return: the grid which is concatenated at the left of this grid
        :rtype: MapSection
        
        """
        return self.__left_grid

    @left_grid.setter
    def left_grid(self, left_grid):
        """
        Setter method for left_grid

        :param left_grid: grid to replace the reference to the current 
                           left grid 
        :type left_grid: MapSection
        :raises TypeError: If the type of the arguments is not MapSection
        
        """
        if type(left_grid) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted, but",
                            type(left_grid), " given.")

        self.__left_grid = left_grid

    @property
    def top_grid(self):
        """
        Getter method for top_grid
    
        :return: the grid which is concatenated at the top of this grid
        :rtype: MapSection
        
        """
        return self.__top_grid

    @top_grid.setter
    def top_grid(self, top_grid):
        """
        Setter method for top_grid

        :param top_grid: grid to replace the reference to the current 
                           top grid 
        :type top_grid: MapSection
        :raises TypeError: If the type of the arguments is not MapSection
        
        """
        if type(top_grid) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted, but",
                            type(top_grid), " given.")

        self.__top_grid = top_grid

    @property
    def bottom_grid(self):
        """
        Getter method for bottom_grid
    
        :return: the grid which is concatenated at the bottom of this grid
        :rtype: MapSection
        
        """
        return self.__bottom_grid

    @bottom_grid.setter
    def bottom_grid(self, bottom_grid):
        """
        Setter method for bottom_grid

        :param bottom_grid: grid to replace the reference to the current 
                           bottom grid 
        :type bottom_grid: MapSection
        :raises TypeError: If the type of the arguments is not MapSection
        
        """
        if type(bottom_grid) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted, but",
                            type(bottom_grid), " given.")

        self.__bottom_grid = bottom_grid

    def update_grid(self, points):
        """
        Updates the grid by increasing the values of the given points.

        :param points: points that shall be updated
        :type points: [[int, int]]
        :raises TypeError: If the type of the arguments is not a list of
                           integer tuple
        
        """
        if type(points) != type([]):
            raise TypeError("Type \"list\" excepted, but",  type(points),
                            " given.")

        for i in range (0, len(points)):
            if len(points[i]) != 2:
                raise TypeError("Wrong format!")

        for i in range (0, len(points)):
            self.__grid[points[i][0]][points[i][1]] += 1

    def print_grid(self):
        """
        Auxiliary function which prints the current grid in the console.

        """
        line = ""
        for i in range(0, self.__GRID_HEIGHT):
            for j in range(0, self.__GRID_WIDTH):
                line += str(self.__grid[i][j]) + "\t"
            print line
            line = ""
