"""
Module for utilities

"""

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
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.yaw = yaw
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