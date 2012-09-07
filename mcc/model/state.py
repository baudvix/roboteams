"""
state represents the MetaStateMachine with its definitions for the trigger to
get to the next state.
"""

STATE_INIT = 0
STATE_AUTONOM_EXPLORATION = 1
STATE_GUIDED_EXPOLRATION = 2
STATE_PATH_VERIFICATION = 3
STATE_NAOWALK = 4


class StateMachine(object):
    """
    Class for the state machine

    """

    def __init__(self, start_state=STATE_INIT):
        """
        Creates a state machine

        :return: 'StateMachine' in the initial state
        :rtype: StateMachine

        """
        self.__state = start_state

    #PROPERTY --- state
    def fget_state(self):
        """The state property getter"""
        return self.__state

    def fset_state(self, value):
        """The state property setter"""
        self.__state = value
    state = property(fget_state, fset_state)
