import math


class Interpolate(object):
    """

    """

    def __init__(self, points, fixed_last_point):
        """
        :param points: list of points of the driven path
        :type points: list
        :param points: list of points of the driven path
        :type points: list
        """

        self.__distance = 0
        self.__points = points
        self.__weights = []
        self.__x_deviation = fixed_last_point[0] - points[len(points) - 1].position.x_coord
        self.__y_deviation = fixed_last_point[1] - points[len(points) - 1].position.y_coord

        # Compute complete distance along the path
        for i in range(0, len(self.__points) - 1):
            self.__distance += self.point_distance(self.__points[i], self.__points[i + 1])

    def run(self):
        self.__weights.append(0)

        # -- Compute weights
        distance = 0

        for i in range(0, len(self.__points) - 1):
            distance += self.point_distance(self.__points[i], self.__points[i + 1])
            self.__weights.append(distance / self.__distance)

        # -- Adjust points
        for i in range(0, len(self.__points)):
            self.__points[i].position.x_coord = int(self.__points[i].position.x_coord + (self.__x_deviation * self.__weights[i]))
            self.__points[i].position.y_coord = int(self.__points[i].position.y_coord + (self.__y_deviation * self.__weights[i]))

        return self.__points

    def point_distance(self, point_1, point_2):

        x1 = point_1.position.x_coord
        x2 = point_2.position.x_coord
        y1 = point_1.position.y_coord
        y2 = point_2.position.y_coord

        distance = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
        return distance

if __name__ == '__main__':
    from mcc.utils import Point
    from mcc.model import map
    from mcc.model.robot import DataNXT
    points = [DataNXT(Point(0, 0, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT)]
    points.append(DataNXT(Point(10, 10, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    points.append(DataNXT(Point(20, 20, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    points.append(DataNXT(Point(30, 110, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    points.append(DataNXT(Point(40, 20, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    points.append(DataNXT(Point(50, 10, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    points.append(DataNXT(Point(60, 0, 0), map.POINT_FREE, DataNXT.DATA_NXT_CURRENT))
    test = Interpolate(points, [50, 10])

    def print_points(ppoints):
        for p in range(0, len(ppoints)):
            print '(%d,%d)' % (ppoints[p].position.x_coord, ppoints[p].position.y_coord)

    print_points(points)
    print_points(test.run())
