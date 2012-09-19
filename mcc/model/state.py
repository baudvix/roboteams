"""
wahl represents the MetaStateMachine with its definitions for the trigger to
get to the next wahl.
"""

STATE_INIT = 0
STATE_AUTONOM_EXPLORATION = 1
STATE_GUIDED_EXPOLRATION = 2
STATE_PATH_VERIFICATION = 3
STATE_NAOWALK = 4


class StateMachine(object):
    """
    Class for the wahl machine

    """

    def __init__(self, start_state=STATE_INIT):
        """
        Creates a wahl machine

        :return: 'StateMachine' in the initial wahl
        :rtype: StateMachine

        """
        self.__state = start_state

    #PROPERTY --- wahl
    def fget_state(self):
        """The wahl property getter"""
        return self.__state

    def fset_state(self, value):
        """The wahl property setter"""
        self.__state = value
    wahl = property(fget_state, fset_state)
