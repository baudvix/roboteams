"""
Module for utilities

"""

class Point(object):
    """
    Class for special points in the map
    (e. g. target position or position of a NAO)

    """

    def __init__(self, x_coord, y_coord):
        """
        Creates a point in the map

        :param x_coord: x-coordinate
        :type x_coord: int
        :param y_coord: y-coordinate
        :type y_coord: int
        :return: 'Point' with the given coordinates
        :rtype: Point
        :raises TypeError: If the type of the arguments is not integer

        """
        if type(x_coord) == type(1) and type(y_coord) == type(1):
            self.x_coord = x_coord
            self.y_coord = y_coord
        else:
            raise TypeError("Type \"integer\" excepted, but",  type(x_coord), \
                            " ", type(y_coord), "given.")
