import math


class UpdateNXTData(object):
    """


    """

    def __init__(self):
        """
        Initialises an object to fill a map with points, passed by an NXT
        Each object must be used for exact one NXT

        """
        self.__nxt_width = 9
        self.__nxt_height = 15
        self.__points_per_second = 0.5
        self.__nxt_speed = 5
        self.__points = []
        self.__points_max = 5
        self.__filled = []
        self.__filled_max = int(self.__nxt_width * self.__nxt_height * 3)
        self.__corner_radius = math.sqrt(math.pow(self.__nxt_height / 2, 2) + math.pow(self.__nxt_width / 2, 2))
        self.__angel = math.atan((self.__nxt_width / 2.0) / (self.__nxt_height / 2.0))

    def insert_position_data(self, x_coord, y_coord, yaw):
        """
        Computes the new points to be added to the map

        :param x_coord: x-coordinate
        :type x_coord; int
        :param y_coord: y-coordinate
        :type y_coord; int
        :param yaw: yaw
        :type yaw; int
        :return: a list of points
        :rtype: list
        """

        corners = self.compute_rotation(x_coord, y_coord, yaw)

        #first insert
        new_points = self.relative_complement(self.fill_polygon(corners), self.__filled)
        for point in new_points:
            self.get_put(self.__filled, point, self.__filled_max)
        self.get_put(self.__points, [x_coord, y_coord], self.__points_max)
        self.__filled = self.sort_by_distance(self.__filled, [x_coord, y_coord])

        return new_points

    def compute_rotation(self, x_coord, y_coord, yaw, option=0):
        """
        Computes the corners of the NXT

        :param x_coord: x-coordinate
        :type x_coord; int
        :param y_coord: y-coordinate
        :type y_coord; int
        :param yaw: yaw
        :type yaw; int
        :param option: 0: compute all 4 corners; 1: compute front right and left only
        :type option: int
        :return; a list of points
        :rtype: list
        """

        front_left = [int(math.cos(yaw + self.__angel) * self.__corner_radius + x_coord),
                      int(math.sin(yaw + self.__angel) * self.__corner_radius + y_coord)]
        front_right = [int(math.cos(yaw - self.__angel) * self.__corner_radius + x_coord),
                       int(math.sin(yaw - self.__angel) * self.__corner_radius + y_coord)]
        if option:
            return [front_right, front_left]

        back_left = [int(math.cos(yaw - math.pi + self.__angel) * self.__corner_radius + x_coord),
                      int(math.sin(yaw - math.pi + self.__angel) * self.__corner_radius + y_coord)]
        back_right = [int(math.cos(yaw - math.pi - self.__angel) * self.__corner_radius + x_coord),
                       int(math.sin(yaw - math.pi - self.__angel) * self.__corner_radius + y_coord)]

        return [front_right, front_left, back_right, back_left]

    def bresenham(self, x0, y0, x1, y1):
        """
        Bresenham's algorithm to compute lines in the grid

        :param x0: x-coordinate 1
        :type x0; int
        :param y0: y-coordinate 1
        :type y0; int
        :param x1: x-coordinate 2
        :type x1; int
        :param y1: y-coordinate 2
        :type y1; int
        :return: list of points
        :rtype; list
        """

        result = []
        dx = math.fabs(x1 - x0)
        if x0 < x1:
            sx = 1
        else:
            sx = -1
        dy = math.fabs(y1 - y0) * (-1)
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

    def fill_polygon(self, corners):
        """
        Computes the points in the polygon given by the corners
        Triangles and rectangles allowed

        :param corners: corners of the polygon (3-4)
        :type corners: list
        :return: list of points in the polygon
        :rtype: list
        """

        result = []
        start = None
        result.extend(self.bresenham(corners[0][0], corners[0][1], corners[1][0], corners[1][1]))
        result.extend(self.bresenham(corners[1][0], corners[1][1], corners[2][0], corners[2][1]))
        if len(corners) == 3:
            result.extend(self.bresenham(corners[2][0], corners[2][1], corners[0][0], corners[0][1]))
            mid_x = (corners[0][0] + corners[1][0] + corners[2][0]) / 3
            mid_y = (corners[0][1] + corners[1][1] + corners[2][1]) / 3
            start = [mid_x, mid_y]
        elif len(corners) == 4:
            result.extend(self.bresenham(corners[2][0], corners[2][1], corners[3][0], corners[3][1]))
            result.extend(self.bresenham(corners[3][0], corners[3][1], corners[0][0], corners[0][1]))
            mid_x = (corners[0][0] + corners[1][0] + corners[2][0] + corners[3][0]) / 4
            mid_y = (corners[0][1] + corners[1][1] + corners[2][1] + corners[3][1]) / 4
            start = [mid_x, mid_y]

        inner_points = [start]
        for point in inner_points:
            if not ([point[0] + 1, point[1]] in result or [point[0] + 1, point[1]] in inner_points):
                inner_points.append([point[0] + 1, point[1]])
            if not ([point[0], point[1] + 1] in result or [point[0], point[1] + 1] in inner_points):
                inner_points.append([point[0], point[1] + 1])
            if not ([point[0] - 1, point[1]] in result or [point[0] - 1, point[1]] in inner_points):
                inner_points.append([point[0] - 1, point[1]])
            if not ([point[0], point[1] - 1] in result or [point[0], point[1] - 1] in inner_points):
                inner_points.append([point[0], point[1] - 1])

        result.extend(inner_points)
        return self.remove_duplicates(result)

    def get_put(self, list, element, max_size):
        """
        Put 'element' in 'list' and removes the last element if max_size is reached

        :param list; the list
        :type list: list
        :param element: the element
        :type element: list
        """

        if len(list) == max_size:
            list.pop()
            list.insert(0, element)
        else:
            list.insert(0, element)

    def remove_duplicates(self, list):
        """
        Removes the duplicate entries in the given list

        :param list: the list
        :type list: list
        :return: the list without duplicate entries
        :rtype: list
        """

        result = []
        for element in list:
            if element not in result:
                result.append(element)
        return result

    def relative_complement(self, list_1, list_2):
        """
        Computes the relative complement (sets) of the two given lists

        :param list_1: list 1
        :type list_1; list
        :param list_2: list 2
        :type list_2; list
        :return: the relative complement of list_1 relative to list_2
        :rtype: list
        """

        delete = []
        for element in list_1:
            if element in list_2:
                delete.append(element)
        for element in delete:
            if element in list_1:
                list_1.remove(element)
        return list_1


    def point_distance(self, point_1, point_2):
        """

        """
        x1 = point_1[0]
        x2 = point_2[0]
        y1 = point_1[1]
        y2 = point_2[1]

        distance = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
        return distance


    def merge(self, left, right, bench_mark):
        """

        """

        result = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            if self.point_distance(left[i], bench_mark) <= self.point_distance(right[j], bench_mark):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result += left[i:]
        result += right[j:]
        return result


    def sort_by_distance(self, points, bench_mark):
        """
        :param points: list of points to be sorted
        :type points: list
        :param bench_mark: bench mark
        :type bench_mark: list
        """

        if len(points) < 2:
            return points
        middle = len(points) / 2
        left = self.sort_by_distance(points[:middle], bench_mark)
        right = self.sort_by_distance(points[middle:], bench_mark)
        return self.merge(left, right, bench_mark)