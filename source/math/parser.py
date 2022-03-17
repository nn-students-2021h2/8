"""
An abstract class represents parser for user input
"""
import difflib
import re
from abc import ABC, abstractmethod

import sympy as sy
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, standard_transformations

from source.extras.translation import _


class ParseError(Exception):
    """This exception will be thrown when something went wrong while parsing"""


class Parser(ABC):
    """
    Contains common methods that can be used in GraphParser and CalculusParser (and other in the future)
    """

    # The accuracy of the prediction system. The bigger the number, the more similar the words need to be to correct it
    PREDICTION_ACCURACY = 0.7

    def __init__(self):
        self._warnings = []

    @abstractmethod
    def parse(self, query: str, lang: str = 'en'):
        """Function that parses user input. Should be redefined in children classes"""

    @staticmethod
    def is_x_equal_num_expression(token: str) -> bool:
        """
        The function checks if expression is like "x = 1"
        :param token: string expression
        :return: true or false
        """
        y = sy.Symbol('y')
        result = False
        parts = token.split('=')
        rules = standard_transformations + (implicit_multiplication_application, convert_xor)
        if len(parts) == 2:
            first_part = sy.parse_expr(parts[0], transformations=rules)
            second_part = sy.parse_expr(parts[1], transformations=rules)
            symbols = first_part.free_symbols | second_part.free_symbols
            result = len(symbols) == 1 and symbols != {y}

        return result

    @property
    def warnings(self) -> list:
        """
        Warnings getter
        :return: warnings as a list
        """
        return self._warnings

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

    def _fix_words(self, query: str, pattern_set: str, pattern_dict: dict, lang: str = "en") -> str:
        """
        Tries to correct words to fit the pattern based on keywords of pattern
        :param lang:
        :param query: query to fix
        :param pattern_set: a class of query
        :param pattern_dict: a dictionary where the keywords are
        :return: if query was corrected, then function returns corrected string, else returns empty string
        """
        # Pick up words with length more than 2 chars
        query_words = [word for word in re.split("[ =]", query) if len(word) > 2]
        pattern_words = pattern_dict[pattern_set]["keywords"]
        result = query

        # Tries to find similar words and replace old ones with them in result
        for word in query_words:
            matches = difflib.get_close_matches(word, pattern_words, n=1, cutoff=self.PREDICTION_ACCURACY)
            if len(matches) == 1 and matches[0] != word:
                result = result.replace(word, str(matches[0]))
                self.push_warning(_("Interpreting '{}' as '{}'", locale=lang).format(word, matches[0]))

        return result if result != query else ""
