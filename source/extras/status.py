"""File contain class Status, that use as finite state machine"""
from enum import Enum
from functools import total_ordering


@total_ordering
class Status(Enum):
    """Enum for define statuses of chat"""
    MAIN = 0
    GRAPH = 1
    ANALYSE = 2
    DERIVATIVE = 3
    DOMAIN = 4
    RANGE = 5
    ZEROS = 6
    AXES_INTERSECTION = 7
    PERIODICITY = 8
    CONVEXITY = 9
    CONCAVITY = 10
    MONOTONICITY = 11
    V_ASYMPTOTES = 12
    H_ASYMPTOTES = 13
    S_ASYMPTOTES = 14
    ASYMPTOTES = 15
    EVENNESS = 16
    ODDNESS = 17
    MAXIMUM = 18
    MINIMUM = 19
    STATIONARY_POINTS = 20
    ANALYSE_MENU = 21
    SETTINGS = 22

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
