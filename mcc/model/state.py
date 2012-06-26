"""
state represents the MetaStateMachine with its definitions for the trigger to
get to the next state.
"""


class StateMachine(object):
    """
    Class for the state machine

    """

    def __init__(self):
        """
        Creates a state machine

        :return: 'StateMachine' in the initial state
        :rtype: StateMachine

        """
        self.__state = 0
