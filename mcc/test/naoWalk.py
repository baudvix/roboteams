from mcc.utils import *
import random

class NaoWalk(object):
    """
        PSEUDOCODE:


        1. Für n Punkte p die zufällig aus den punkten ausgewählt werden, die Frei sind:
            - Setze Linien und such dir die kürzeste raus
            - packe den punkt p auf den Mittelpunkt der Linie mit dem Radius r
            - prüfe ob der kreis einen schwarzen berreich berrührt. wenn ja -> mache den radius kleiner und teste nochmal
        2. Verbinde alle punkte, die sich überschneiden.
        3. Prüfe, ob die überschneidungen groß genug sind. -> füge einen extra punkt in der mitte ein und baue einen radius

        PROBLEME:
        - wie n(p.length) bestimmen?
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

        #TestVariables
        # Dimensionen der Karte
        self.dimLeft = 1
        self.dimRight = 1
        self.dimTop = 1
        self.dimBottom = 0


    def run(self):
        """

        """


    def random_point(self):
        """

        """

        random_x = random.r

        return random.randint(0, len(self.__free_space))

