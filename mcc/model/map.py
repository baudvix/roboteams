#!/usr/bin/env python
"""
map holds a model of the map, where the data of the NXT is finally stored
"""

from mcc import utils
import threading

POINT_FREE = 0
POINT_TARGET = 1
POINT_DODGE_LEFT = 2
POINT_DODGE_CENTER = 3
POINT_DODGE_RIGHT = 4


class MapModel(object):
    """
    Class for the MapModel. Contains the reference to the first map section
    which contains the position of the NAO.

    """

    def __init__(self, name):
        """
        Creates a map model

        :return: 'MapModel' with an initial map section ('first_map_section')
                 and a target position ('target_position')
        :rtype: MapModel

        """
        self.__first_map_section = MapSection()
        self.__target_position = None
        self.name = name
        self._lock = threading.Lock()

    def get_first_map_section(self):
        """
        Getter method for first_map_section

        :return: first map section in the map model
        :rtype: MapSection

        """
        with self._lock:
            return self.__first_map_section

    def set_first_map_section(self, map_section):
        """
        Setter method for first_map_section

        :param map_section: map section to replace the current
        :type map_section: MapSection
        :raises TypeError: If the type of the arguments is not MapSection

        """
        if type(map_section) != type(MapSection()):
            raise TypeError("Type \"MapSection\" excepted,\
                             but",  type(map_section), " given.")
        with self._lock:
            self.__first_map_section = map_section

    first_map_section = property(get_first_map_section, set_first_map_section)

    def get_target_position(self):
        """
        Getter method for target_position

        :return: position of the target in the map model
        :rtype: Point

        """
        with self._lock:
            return self.__target_position

    def set_target_position(self, target_position):
        """
        Setter method for target_position

        :param target_position: point to replace the current target position
        :type target_position: Point
        :raises TypeError: If the type of the arguments is not Point

        """
        if type(target_position) != type(utils.Point(0, 0, 0)):
            raise TypeError("Type \"Point\" excepted, but",
                type(target_position), " given.")
        with self._lock:
            self.__target_position = target_position

    target_position = property(get_target_position, set_target_position)

    def _add_map_section(self, offset_x, offset_y):
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
            for _ in range(0, offset_x):
                if tmp_map_section.right_grid is None:
                    tmp_map_section.right_grid = MapSection()
                tmp_map_section = tmp_map_section.right_grid
        elif offset_x < 0:
            for _ in range(0, offset_x, -1):
                if tmp_map_section.left_grid is None:
                    tmp_map_section.left_grid = MapSection()
                tmp_map_section = tmp_map_section.left_grid
        if offset_y > 0:
            for _ in range(0, offset_y):
                if tmp_map_section.top_grid is None:
                    tmp_map_section.top_grid = MapSection()
                tmp_map_section = tmp_map_section.top_grid
        elif offset_y < 0:
            for _ in range(0, offset_y, -1):
                if tmp_map_section.bottom_grid is None:
                    tmp_map_section.bottom_grid = MapSection()
                tmp_map_section = tmp_map_section.bottom_grid

        if (offset_x > 0 and tmp_map_section.right_grid is not None) or\
           (offset_x < 0 and tmp_map_section.left_grid is not None) or\
           (offset_y > 0 and tmp_map_section.top_grid is not None) or\
           (offset_y < 0 and tmp_map_section.bottom_grid is not None):
            raise ValueError("Can't add MapSection with this offset - \
                             position is occupied.")

    def get_point(self, x_coord, y_coord):
        """
        Returns the value of a given point and creates a map section, if
        necessary

        :param x_coord: the x-coordinate of which the value shall be returned
        :type x_coord: int
        :param y_coord: the y-coordinate of which the value shall be returned
        :type y_coord: int
        :return: the value of the point
        :rtype: int

        """
        if type(x_coord) != type(1) or type(y_coord) != type(1):
            raise TypeError("Type \"int\" excepted, but", type(x_coord), ", ",
                type(y_coord), " given.")

        offset_x = x_coord / MapSection.get_grid_width()
        offset_y = y_coord / MapSection.get_grid_height()
        x_abs = x_coord % MapSection.get_grid_width()
        y_abs = y_coord % MapSection.get_grid_height()

        # make sure that the grid exists; pass if it already does
        try:
            with self._lock:
                self._add_map_section(offset_x, offset_y)
        except ValueError:
            pass

        tmp_map_section = self.__first_map_section

        if offset_x > 0:
            for _ in range(0, offset_x):
                tmp_map_section = tmp_map_section.right_grid
        elif offset_x < 0:
            for _ in range(0, offset_x, -1):
                tmp_map_section = tmp_map_section.left_grid
        if offset_y > 0:
            for _ in range(0, offset_y):
                tmp_map_section = tmp_map_section.top_grid
        elif offset_y < 0:
            for _ in range(0, offset_y, -1):
                tmp_map_section = tmp_map_section.bottom_grid

        with self._lock:
            return tmp_map_section.get_point_value(x_abs, y_abs)

    def set_point(self, x_coord, y_coord, option=0):
        """
        Increases the value of a given point or sets a dodge point
        and creates a map section, if necessary

        :param x_coord: the x-coordinate of which the value shall be increased
        :type x_coord: int
        :param y_coord: the y-coordinate of which the value shall be increased
        :type y_coord: int
        :param option: 0: free point, 1: dodge point
        :type option: int

        """
        if type(x_coord) != type(1) or type(y_coord) != type(1) or \
           type(option) != type(1):
            raise TypeError("Type \"int\" excepted, but", type(x_coord), ", ",
                  type(y_coord), ", ", type(option), " given.")

        offset_x = x_coord / MapSection.get_grid_width()
        offset_y = y_coord / MapSection.get_grid_height()
        x_abs = x_coord % MapSection.get_grid_width()
        y_abs = y_coord % MapSection.get_grid_height()

        # make sure that the grid exists; pass if it already does
        try:
            with self._lock:
                self._add_map_section(offset_x, offset_y)
        except ValueError:
            pass

        tmp_map_section = self.__first_map_section

        if offset_x > 0:
            for _ in range(0, offset_x):
                tmp_map_section = tmp_map_section.right_grid
        elif offset_x < 0:
            for _ in range(0, offset_x, -1):
                tmp_map_section = tmp_map_section.left_grid
        if offset_y > 0:
            for _ in range(0, offset_y):
                tmp_map_section = tmp_map_section.top_grid
        elif offset_y < 0:
            for _ in range(0, offset_y, -1):
                tmp_map_section = tmp_map_section.bottom_grid
        with self._lock:
            if option == 0:
                tmp_map_section.update_grid([[x_abs, y_abs]])
            elif option == 1 and tmp_map_section.get_point_value(x_abs, y_abs, 1) != 1:
                tmp_map_section.update_grid([[x_abs, y_abs]], 1)

    def increase_points(self, points):
        """
        Increases the values of the given points and creates a map section, if
        necessary

        :param points: a list of points of which the value shall be increased
        :type points: list

        """
        if type(points) != type([]):
            raise TypeError("Type \"list\" excepted, but", type(points), ", ",
                            " given.")

        with self._lock:
            for p in points:
                self.set_point(p[0], p[1])


class MapSection(object):
    """
    Class for the MapSection. Contains the references to the bordering grids
    and the grid which is defined by 'grid_height' and 'grid_width'
    Grid holds [free, dodge] count
    """
    __grid_height = 100
    __grid_width = 100

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

        self.__grid = []

        # initialize grid with zeros
        for i in range(0, MapSection.__grid_height):
            self.__grid.append([])
            for _ in range(0, MapSection.__grid_width):
                self.__grid[i].append([0, 0])

    def get_right_grid(self):
        """
        Getter method for right_grid

        :return: the grid which is concatenated at the right of this grid
        :rtype: MapSection

        """
        return self.__right_grid

    def set_right_grid(self, right_grid):
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

    right_grid = property(get_right_grid, set_right_grid)

    def get_left_grid(self):
        """
        Getter method for left_grid

        :return: the grid which is concatenated at the left of this grid
        :rtype: MapSection

        """
        return self.__left_grid

    def set_left_grid(self, left_grid):
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

    left_grid = property(get_left_grid, set_left_grid)

    def get_top_grid(self):
        """
        Getter method for top_grid

        :return: the grid which is concatenated at the top of this grid
        :rtype: MapSection

        """
        return self.__top_grid

    def set_top_grid(self, top_grid):
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

    top_grid = property(get_top_grid, set_top_grid)

    def get_bottom_grid(self):
        """
        Getter method for bottom_grid

        :return: the grid which is concatenated at the bottom of this grid
        :rtype: MapSection

        """
        return self.__bottom_grid

    def set_bottom_grid(self, bottom_grid):
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

    bottom_grid = property(get_bottom_grid, set_bottom_grid)

    def get_grid_height():
        """
        Getter method for grid_height

        :return: the grids height
        :rtype: int

        """
        return MapSection.__grid_height

    get_grid_height = staticmethod(get_grid_height)

    def get_grid_width():
        """
        Getter method for grid_width

        :return: the grids width
        :rtype: int

        """
        return MapSection.__grid_width

    get_grid_width = staticmethod(get_grid_width)

    def get_point_value(self, x_coord, y_coord, option=0):
        """
        :param x_coord: x_coord where the value shall be retrieved of
        :type x_coord: int
        :param y_coord: y_coord where the value shall be retrieved of
        :type y_coord: int
        :param option: 0: Point value; 1: Dodge value
        :type option: int
        :raises TypeError: If the type of the arguments is not int

        """
        if type(x_coord) != type(1) or type(y_coord) != type(1) or type(option) != type(1):
            raise TypeError("Type \"int\" excepted, but", type(x_coord),
                ", ", type(y_coord), ", ", type(option), " given.")

        if option == 0:
            return self.__grid[x_coord][y_coord][0]
        else:
            return self.__grid[x_coord][y_coord][1]

    def update_grid(self, points, option=0):
        """
        Updates the grid by increasing the values of the given points
        or marking / deleting a dodge

        :param points: points that shall be updated
        :type points: list
        :param option: 0: Point values; 1: Dodge values
        :type option: int
        :raises TypeError: If the type of the arguments is not a list of
                           integer tuple and an int

        """
        if type(points) != type([]):
            raise TypeError("Type \"list\", \"int\" excepted, but", type(points),
                            ", ", type(option), " given.")

        for i in range(0, len(points)):
            if len(points[i]) != 2:
                raise TypeError("Wrong format!")

        if not option:
            for i in range(0, len(points)):
                self.__grid[points[i][0]][points[i][1]][0] += 1
        else:
            for i in range(0, len(points)):
                if not self.__grid[points[i][0]][points[i][1]][1]:
                    self.__grid[points[i][0]][points[i][1]][1] = 1
                else:
                    self.__grid[points[i][0]][points[i][1]][1] = 0
