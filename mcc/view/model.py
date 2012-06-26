"""
Module for the model

"""
from mcc.view.view import View
from state import StateMachine
from map import MapModel


class Model(object):
    """
    Class for the model. Contains the references to the MapModel,the NAOModels,
    the NXTModels, the views and the state machine

    """

    def __init__(self):
        """
        Creates a model

        :return: 'Model' with an initial map model ('map_model'), a view
                 ('view') and a state machine ('state_machine')
        :rtype: Model

        """
        self.__map_model = MapModel()
        self.__nao_model = [None]
        self.__nxt_model = [None]
        self.__view = View(self.__map_model)
        self.__state_machine = StateMachine()

    def register_nao(self):
        pass

    def register_nxt(self):
        pass
