"""
Module for utilities
"""

import math

class Point(object):
    """
    Class for special points in the map
    (e. g. target position or position of a NAO)
    """

    def __init__(self, x_coord, y_coord, yaw=0):
        """
        Creates a point in the map

        :param x_coord: x-coordinate
        :type x_coord: int
        :param y_coord: y-coordinate
        :type y_coord: int
        :param yaw: yaw of the object
        :type yaw: float
        :return: 'Point' with the given coordinates
        :rtype: Point
        :raises TypeError: If the type of the arguments is not integer

        """
        if (type(x_coord) == type(1)) and (type(y_coord) == type(1)) \
            and (type(yaw) == type(1.0) or type(yaw) == type(1)):
            self.__x_coord = x_coord
            self.__y_coord = y_coord
            self.__yaw = yaw
        else:
            raise TypeError("Type \"integer / float\" excepted, but",
                            type(x_coord), " ", type(y_coord), " ",
                            type(y_coord), "given.")

    def get_x_coord(self):
        """
        Getter method for x_coord

        :return: x-coordinate of the point
        :rtype: int

        """
        return self.__x_coord

    def set_x_coord(self, x_coord):
        """
        Setter method for x_coord

        :param x_coord: new x-coordinate of the point
        :type x_coord: int
        :raises TypeError: If the type of the arguments is not int

        """
        if type(x_coord) != type(1):
            raise TypeError("Type \"int\" excepted, but",
                type(x_coord), " given.")

        self.__x_coord = x_coord

    x_coord = property(get_x_coord, set_x_coord)

    def get_y_coord(self):
        """
        Getter method for y_coord

        :return: y-coordinate of the point
        :rtype: int

        """
        return self.__y_coord

    def set_y_coord(self, y_coord):
        """
        Setter method for y_coord

        :param y_coord: new y-coordinate of the point
        :type y_coord: int
        :raises TypeError: If the type of the arguments is not int

        """
        if type(y_coord) != type(1):
            raise TypeError("Type \"int\" excepted, but",
                type(y_coord), " given.")

        self.__y_coord = y_coord

    y_coord = property(get_y_coord, set_y_coord)

    def get_yaw(self):
        """
        Getter method for yaw

        :return: yaw of the point
        :rtype: float

        """
        return self.__yaw

    def set_yaw(self, yaw):
        """
        Setter method for yaw

        :param yaw: new yaw of the point
        :type yaw: float
        :raises TypeError: If the type of the arguments is not float

        """
        if type(yaw) != type(1.0) or type(yaw) != type(1):
            raise TypeError("Type \"float\" excepted, but",
                            type(yaw), " given.")

        self.__yaw = yaw

    yaw = property(get_yaw, set_yaw)


class Color():
    """
    Holds the static color definitions
    """
    COLOR_NONE = -1
    COLOR_RED = 0
    COLOR_GREEN = 1
    COLOR_BLUE = 2
    COLOR_YELLOW = 3
    COLOR_BLACK = 4

    @staticmethod
    def is_color(color):
        if Color.COLOR_NONE <= color and color <= Color.COLOR_BLACK:
            return True
        else:
            return False



def merge(left, right, bench_mark, order):
    """

    """

    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if not order:
            if point_distance(left[i], bench_mark) <= point_distance(right[j], bench_mark):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if point_distance(left[i], bench_mark) >= point_distance(right[j], bench_mark):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1


    result += left[i:]
    result += right[j:]
    return result


def sort_by_distance(points, bench_mark, order = 0):
    """
    :param points: list of points to be sorted
    :type points: list
    :param bench_mark: bench mark
    :type bench_mark: list
    :param order: ascending order (0) or descending order (1)
    """

    if len(points) < 2:
        return points
    middle = len(points) / 2
    left = sort_by_distance(points[:middle], bench_mark, order)
    right = sort_by_distance(points[middle:], bench_mark, order)

    return merge(left, right, bench_mark, order)


def point_distance(point_1, point_2):

    x1 = point_1[0]
    x2 = point_2[0]
    y1 = point_1[1]
    y2 = point_2[1]

    distance = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
    return distance

