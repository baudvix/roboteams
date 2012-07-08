from mcc.model.map import *
from mcc.simulator.fake import *
from mcc.utils import *
import math

class FindFreeSpace(object):
    """

    """

    def __init__(self, map, nxt=None):
        """
        :param map: Map to be used
        :type map: MapModel
        :param nxt: NXTs used in the Scenario
        :type nxt: NXTModel
        """

        #TODO map, nxt parent (controller)?
        self.map = map
        self.nxt = nxt
        self.boundaries = []
        self.amount = 5000

    def run(self):
        #TODO find boundaries from each NXT starting point
        self.boundaries.append(self.find_boundary(10, 10))
        self.boundaries.append(self.find_boundary(50, 60))

        #TODO ensure that, if a boundary covers more than one starting point,
        #TODO the boundary is not computed twice

        start = self.compute_center()
        x_start = (start[0][0] + start[1][0]) / 2
        y_start = (start[0][1] + start[1][1]) / 2
        return self.find_target_points(x_start, y_start)

    def find_boundary(self, x_coord, y_coord):
        """

        """
        x = x_coord
        y = y_coord
        boundary = []
        #TODO NXT start position, parameter
        # 0: up, 1: right, 2: down, 3: left
        last_direction = 4
        i = 0
        while True:
            if i > 50:
                boundary = [[100, 100]]
                break
            if self.check_point(x, y + 1) > 0 and \
               not boundary.__contains__([x, y + 1]) and last_direction != 2:
                y += 1
                last_direction = 0
            elif self.check_point(x + 1, y) > 0 and \
                 not boundary.__contains__([x + 1, y]) and last_direction != 3:
                x += 1
                last_direction = 1
            elif self.check_point(x, y - 1) > 0 and \
                 not boundary.__contains__([x, y - 1]) and last_direction != 0:
                y -= 1
                last_direction = 2
            elif self.check_point(x - 1, y) > 0 and \
                 not boundary.__contains__([x - 1, y]) and last_direction != 1:
                x -= 1
                last_direction = 3
            else:
                x += 1
                last_direction = 1
                i += 1
                continue
            boundary.append([x, y])
            if x == x_coord and y == y_coord:
                break
            i += 1

        return boundary


    def check_point(self, x_coord, y_coord):
        """
        Checks whether the given point has a value unequal zero and has points
        with value zero in its surrounding area

        :param x_coord: The x-coordinate of the point
        :type x_coord: int
        :param y_coord: The y-coordinate of the point
        :type y_coord: int
        :return: The number of points with an edge at the given point and
                 value 0
        :rtype: int
        """

        count = 0
        if not self.map.get_point(x_coord, y_coord):
            return 0
        if not self.map.get_point(x_coord + 1, y_coord):
            count += 1
        if not self.map.get_point(x_coord, y_coord + 1):
            count += 1
        if not self.map.get_point(x_coord - 1, y_coord):
            count += 1
        if not self.map.get_point(x_coord, y_coord - 1):
            count += 1
        return count


    def compute_center(self):
        """

        """
        central_points = []
        for list in self.boundaries:
            length = 0
            x_value = 0
            y_value = 0
            for point in list:
                length += 1
                x_value += point[0]
                y_value += point[1]
            central_points.append([x_value / length, y_value / length])

        return central_points


    def find_target_points(self, x_start, y_start):
        """

        """

        x_coord = x_start
        y_coord = y_start
        step_size = 1
        # 0: right, 1: up, 2: left, 3: down
        direction = 1
        found_points = 0
        target_points = []
        while True:
            if direction == 0:
                for i in range(0, step_size):
                    x_coord += 1
                    if not self.map.get_point(x_coord, y_coord):
                        target_points.append([x_coord, y_coord])
                        found_points += 1
                direction += 1
            elif direction == 1:
                for i in range(0, step_size):
                    y_coord += 1
                    if not self.map.get_point(x_coord, y_coord):
                        target_points.append([x_coord, y_coord])
                        found_points += 1
                direction += 1
                step_size += 1
            elif direction == 2:
                for i in range(0, step_size):
                    x_coord -= 1
                    if not self.map.get_point(x_coord, y_coord):
                        target_points.append([x_coord, y_coord])
                        found_points += 1
                direction += 1
            elif direction == 3:
                for i in range(0, step_size):
                    y_coord -= 1
                    if self.map.get_point(x_coord, y_coord) == 0:
                        target_points.append([x_coord, y_coord])
                        found_points += 1
                direction = 0
                step_size += 1
            if found_points >= self.amount:
                break

        return target_points


class FindDestinations(object):
    """

    """

    def __init__(self, free_space, nxt_positions):
        """
        :param free_space: List of points which are unexplored yet
        :type free_space: list
        :param nxt_positions: List of positions of the NXTs
        :type nxt_positions: list
        """

        self.__free_space = free_space
        x = y = 0
        for point in self.__free_space:
            x += point[0]
            y += point[1]
        self.__center = [x / len(self.__free_space), y / len(self.__free_space)]
        self.__nxt_positions = nxt_positions
        # Number of areas to be mapped to a NXT
        self.__number_of_areas = len(self.__nxt_positions)
        self.__areas = []
        self.__areas_size = []
        # Which area is mapped to which NXT: key: area, value: NXT
        self.__mapping = []
        for i in range(0, self.__number_of_areas):
            self.__areas.append([])
            if i == self.__number_of_areas - 1:
                self.__areas_size.append(len(self.__free_space) - (len(self.__free_space) / self.__number_of_areas) * i)
            else:
                self.__areas_size.append(len(self.__free_space) / self.__number_of_areas)
            self.__mapping.append([i, i])


    def divide_free_space(self):
        """

        """

        free_space = self.__free_space
        for i in range(0, self.__number_of_areas):
            free_space = sort_by_distance(free_space, self.__center)
            bench_mark = free_space.pop()
            self.__areas[i].append(bench_mark)
            free_space = sort_by_distance(free_space, bench_mark, 1)
            while len(self.__areas[i]) < self.__areas_size[i]:
                self.__areas[i].append(free_space.pop())


    def delegate_free_space(self):
        """

        """

        x = y = 0
        center = []
        distances = []
        nxt_order = []
        for i in range(0, self.__number_of_areas):
            center.append([])
            for point in self.__areas[i]:
                x += point[0]
                y += point[1]

            center[i] = [x / len(self.__free_space), y / len(self.__free_space)]
            distances.append([])
            nxt_order.append([])
            for j in range(0, len(self.__nxt_positions)):
                nxt_order[i].append(j)
                distances[i].append(point_distance(self.__nxt_positions[j], center[i]))

        for i in range(0, self.__number_of_areas):
            for j in range(0, len(self.__nxt_positions) - 1):
                for k in range(0, len(self.__nxt_positions) - 1):
                    if distances[i][k + 1] < distances[i][k]:
                        tmp1 = distances[i][k]
                        tmp2 = nxt_order[i][k]
                        distances[i][k] = distances[i][k + 1]
                        nxt_order[i][k] = nxt_order[i][k + 1]
                        distances[i][k + 1] = tmp1
                        nxt_order[i][k + 1] = tmp2

        for i in range(0, self.__number_of_areas):
            self.__mapping[i] = nxt_order[i][0]
            remove = nxt_order[i][0]
            for j in range(i, self.__number_of_areas):
                nxt_order[j] = self.remove_value(nxt_order[j], remove)

        return self.__mapping

    def remove_value(self, list, value):
        """

        """

        for i in range(0, len(list)):
            if list[i] == value:
                list.pop(i)
                return list

    def duplicates(self, list):
        """
        Removes the duplicate entries in the given list

        :param list: the list
        :type list: list
        :return: the list without duplicate entries
        :rtype: list
        """

        result = []
        result2 = []
        for element in list:
            if element not in result:
                result.append(element)
            else:
                result2.append(element)
        return result2
