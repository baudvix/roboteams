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