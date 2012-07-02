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
        self.__x_deviation = fixed_last_point[0] - points[points.__len__() - 1].position.x_coord
        self.__y_deviation = fixed_last_point[1] - points[points.__len__() - 1].position.y_coord

        # Compute complete distance along the path
        for i in range(0, self.__points.__len__() - 1):
            self.__distance += self.point_distance(self.__points[i], self.__points[i + 1])

    def run(self):
        self.__weights.append(0)

        # -- Compute weights
        distance = 0

        for i in range(0, self.__points.__len__() - 1):
            distance += self.point_distance(self.__points[i], self.__points[i + 1])
            self.__weights.append(distance / self.__distance)

        # -- Adjust points
        for i in range(0, self.__points.__len__()):
            self.__points[i].position.x_coord = self.__points[i].position.x_coord + (self.__x_deviation * self.__weights[i])
            self.__points[i].position.y_coord = self.__points[i].position.y_coord + (self.__y_deviation * self.__weights[i])

        return self.__points

    def point_distance(self, point_1, point_2):
        """

        """
        x1 = point_1.position.x_coord
        x2 = point_2.position.x_coord
        y1 = point_1.position.y_coord
        y2 = point_2.position.y_coord

        distance = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
        return distance

if __name__ == '__main__':
    points = [[0, 0], [10, 10], [20, 20], [30, 110], [40, 20], [50, 10], [60, 0]]
    test = Interpolate(points, [50, 10])
    print points
    print test.run()
