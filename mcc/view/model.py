#!/usr/bin/env python
"""

"""


class Model(object):
    """
    Class for the model. Contains the references to the MapModel,the NAOModels,
    the NXTModels, the views and the state machine

    """

    def __init__(self):
        """

        """
        self.map = []
        self.robots_nao = []
        self.robots_nxt = []
        self.state_machine = []

    def register_nao(self, robot_nao):
        self.register_nao.append((robot_nao.handle, robot_nao))

    def register_nxt(self, robot_nxt):
        self.robots_nxt.append((robot_nxt.color, robot_nxt))

    def register_map(self, name, new_map):
        self.map.append((name, new_map))

    def register_state(self, state_machine):
        self.state_machine = state_machine
