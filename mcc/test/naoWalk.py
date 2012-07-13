from mcc.utils import *
import random

class NaoWalk(object):
    """

    """

    def __init__(self, map, free_space, start_position):
        """
        :param map: Map to be used
        :type map: MapModel
        :param free_space: List of coordinates which are not occupied
        :type free_space: List
        :param start_position: Start position of the guiding NXT
        :type start_position: List
        """

        #TODO map, parent (controller)?
        self.__map = map
        self.__free_space = free_space
        self.__start_position = start_position

        self.__


    def run(self):
        """

        """


    def random_point(self):
        """

        """

        return random.randint(0, len(self.__free_space))
