"""
Module for the controller

"""

from mcc.mvc.model import *
from mcc.mvc.view import View

#TODO Only for simulation
from mcc.simulator.simulator import Simulator

class Controller(object):
    """
    Class for the controller

    """

    def __init__(self):
        """
        Creates a controller

        :return: 'Controller' with an initial map section ('first_map_section')
                 and a target position ('target_position')
        :rtype: MapModel

        """

        #TODO private, property
        self.map = MapModel()
        self.view = View(self.map)

        #TODO Only for simulation
        self.sim = Simulator()





