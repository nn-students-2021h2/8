"""
An abstract class represents parser for user input
"""
from abc import ABC, abstractmethod

import sympy as sy

# How many statements (functions, domain, etc.) the Bot can handle
STATEMENTS_LIMIT = 15


class ParseError(Exception):
    """This exception will be thrown when something went wrong while parsing"""


class Parser(ABC):
    """
    Contains common methods that can be used in GraphParser and CalculusParser (and other in the future)
    """

    def __init__(self):
        self._warnings = []

    @abstractmethod
    def parse(self, expression: str):
        """Function that parses user input. Should be redefined in children classes"""

    @staticmethod
    def is_x_equal_num_expression(token: str) -> bool:
        """
        The function checks if expression is like "x = 1"
        :param token: string expression
        :return: true of false
        """
        y = sy.Symbol('y')
        result = False
        parts = token.split('=')
        if len(parts) == 2:
            first_part = sy.simplify(parts[0])
            second_part = sy.simplify(parts[1])
            symbols = first_part.free_symbols | second_part.free_symbols
            result = len(symbols) == 1 and symbols != {y}

        return result

    @property
    def warnings(self) -> list:
        """
        Delete warnings and return its values
        :return: warnings as a list
        """
        warning_list = self._warnings
        return warning_list

    def clear_warnings(self):
        """
        Remove all strings from _warnings list
        """
        self._warnings = []

    def push_warning(self, warning: str):
        """
        Push new string in warnings list
        :param warning: what we warn about
        """
        self._warnings.append(warning)
