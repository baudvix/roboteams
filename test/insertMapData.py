from datetime import datetime
import math

class UpdateNXTData(object):
    """


    """

    def __init__(self):
        """


        :return:
        :rtype:

        """
        self.__nxt_width = 9
        self.__nxt_height = 15
        self.__last_added_points = []
        self.__last_point = []
        self.__corner_radius = math.sqrt(math.pow(self.__nxt_height / 2, 2) + math.pow(self.__nxt_width / 2, 2))
        self.__angel = math.atan((self.__nxt_width / 2.0) / (self.__nxt_height / 2.0))

        self.__result = []

    def insert_position_data(self, x_coord, y_coord, yaw, time):
        """
        :param x_coord: x-coordinate
        :type x_coord; int
        :param y_coord: y-coordinate
        :type y_coord; int
        :param yaw: yaw
        :type yaw; int
        :param time: time and date
        :type x_coord; datetime
        """
        corners = self.compute_rotation(x_coord, y_coord, yaw)

        #first insert
        if self.__last_point.__len__() == 0:
            self.fill_polygon(corners, x_coord, y_coord)


    def compute_rotation(self, x_coord, y_coord, yaw):
        """

        """

        front_left = [int(math.cos(yaw + self.__angel) * self.__corner_radius + x_coord),
                      int(math.sin(yaw + self.__angel) * self.__corner_radius + y_coord)]
        front_right = [int(math.cos(yaw - self.__angel) * self.__corner_radius + x_coord),
                       int(math.sin(yaw - self.__angel) * self.__corner_radius + y_coord)]
        back_left = [int(math.cos(yaw - math.pi + self.__angel) * self.__corner_radius + x_coord),
                      int(math.sin(yaw - math.pi + self.__angel) * self.__corner_radius + y_coord)]
        back_right = [int(math.cos(yaw - math.pi - self.__angel) * self.__corner_radius + x_coord),
                       int(math.sin(yaw - math.pi - self.__angel) * self.__corner_radius + y_coord)]
        return [front_right, front_left, back_right, back_left]

    def bresenham(self, x0, y0, x1, y1):
        """

        """

        result = []
        dx =  math.fabs(x1-x0)
        if x0 < x1:
            sx = 1
        else:
            sx = -1
        dy = math.fabs(y1-y0) * (-1)
        if y0 < y1:
            sy = 1
        else:
            sy = -1
        err = dx + dy
        e2 = 0

        while True:
            result.append([x0, y0])
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > dy:
                err += dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return result

    def fill_polygon(self, corners, x_coord, y_coord):
        """

        """

        result = []
        result.extend(self.bresenham(corners[0][0], corners[0][1], corners[1][0], corners[1][1]))
        result.extend(self.bresenham(corners[0][0], corners[0][1], corners[1][0], corners[1][1]))
        result.extend(self.bresenham(corners[1][0], corners[1][1], corners[2][0], corners[2][1]))
        result.extend(self.bresenham(corners[2][0], corners[2][1], corners[3][0], corners[3][1]))
        result.extend(self.bresenham(corners[3][0], corners[3][1], corners[0][0], corners[0][1]))


        inner_points = [[x_coord, y_coord]]
        for point in inner_points:
            if not (self.contains([point[0] + 1, point[1]], result) or
                    self.contains([point[0] + 1, point[1]], inner_points)):
                inner_points.append([point[0] + 1, point[1]])
            if not (self.contains([point[0], point[1] + 1], result) or
                    self.contains([point[0], point[1] + 1], inner_points)):
                inner_points.append([point[0], point[1] + 1])
            if not (self.contains([point[0] - 1, point[1]], result) or
                    self.contains([point[0] - 1, point[1]], inner_points)):
                inner_points.append([point[0] - 1, point[1]])
            if not (self.contains([point[0], point[1] - 1], result) or
                    self.contains([point[0], point[1] - 1], inner_points)):
                inner_points.append([point[0], point[1] - 1])

        result.extend(inner_points)
        return result


    def contains(self, element, list):
        """

        """

        for elem in list:
            if element == elem:
                return True

        return False

test = UpdateNXTData()

test.insert_position_data(0, 0, math.pi/4, None)




