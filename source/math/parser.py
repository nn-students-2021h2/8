from abc import ABC, abstractmethod

import sympy as sy

# How many statements (functions, domain, etc.) the Bot can handle
STATEMENTS_LIMIT = 15


class ParseError(Exception):
    """This exception will be thrown when something went wrong while parsing"""


class Parser(ABC):
    def __init__(self):
        self._warnings = []

    @abstractmethod
    def parse(self, expression: str):
        pass

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
        warning_list, self._warnings = self._warnings, []
        return warning_list

    def push_warning(self, warning: str):
        self._warnings.append(warning)
