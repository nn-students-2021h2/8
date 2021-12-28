"""
User input parser module
"""

import sympy as sy
from sympy import SympifyError
from sympy.logic.boolalg import BooleanTrue

from math_function import MathFunction


# This exception raise when sympy cannot draw a function plot


class ParseError(Exception):
    """This exception will be thrown when something went wrong while parsing"""


# Foo Range
# Explicit foo
# Implicit foo
class Parser:
    """
    This class represents parser for user input. Now, it parses expressions like:
    x**2 + y^2, x, y = a, x = 1, from -12 to -2

    If parse input into dictionary 'tokens'
    """

    def __init__(self):
        self.tokens = {'range': [], 'explicit': [], 'implicit': [], 'unknown': []}

    def _check_range(self, token):
        if (token.strip().find("from")) == 0:
            definition_area = token.split()
            # if 'from _ to _' construction doesn't contain four words, that it is syntax error
            if len(definition_area) != 4:
                raise ParseError(f"Mistake in function range parameters.\n"
                                 f"Your input: {token.strip()}\n"
                                 f"Please, check your \"from _ to _\" statement.")

            try:
                left = float(definition_area[1])
                right = float(definition_area[3])
            except ValueError as err:
                raise ParseError(f"Mistake in function range parameters.\n"
                                 f"Your input: {token.strip()}\n"
                                 f"Please, check your \"from _ to _\" statement.") from err
            self.tokens['range'] = [left, right]
            return True

        return False

    @staticmethod
    def _check_function(token):
        expr_parts = token.split('=')
        parts_count = len(expr_parts)
        x, y = sy.symbols("x y")
        try:
            if parts_count == 1:
                # Replace every variable, that not equal 'y' or 'x' in left part on 'y'
                function = sy.simplify(expr_parts[0])

                for sym in function.free_symbols:
                    if sym not in (x, y):
                        function = function.replace(sym, x)

            elif parts_count == 2:
                # Replace every variable, that not equal 'y' or 'x' in left part on 'y'
                first_part = sy.simplify(expr_parts[0])
                second_part = sy.simplify(expr_parts[1])

                for sym in first_part.free_symbols:
                    if sym not in (x, y):
                        first_part = first_part.replace(sym, y)

                for sym in second_part.free_symbols:
                    if sym not in (x, y):
                        second_part = second_part.replace(sym, x)

                function = sy.Eq(first_part, second_part)
            else:
                raise ValueError("Mistake in implicit function: Found more than 2 equals.\n"
                                 f"Your input: {token.strip()}\n"
                                 "Please, check your math formula")

            solutions = sy.solve(function, y)
            if len(solutions) == 1:
                function = solutions[0]

            # If parsed result always true or false (e.g. it is not a function at all)
            if function is sy.true or function is sy.false:
                raise ParseError(f"Result of expression '{token}' is always {function}")

            return function
        except SympifyError as err:
            raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                             "Please, check your math formula.") from err

    def parse(self, expr: str):
        """
        This method get string and tries to parse it in several groups (see 'tokens' variable)

        Parameters:
        :param expr:
        :return: parsed user input in the form of dictionary 'tokens'
        """
        x = sy.symbols('x')
        parts = expr.split(',')

        for token in parts:
            # If it is a function range
            try:
                if self._check_range(token):
                    continue
            except ParseError as err:
                raise err

            # If it is a function
            try:
                function = self._check_function(token)
            except ParseError as err:
                raise err

            # Update tokens list
            variables_count = len(function.free_symbols)

            if variables_count > 2:
                # If it is an unknown expression
                self.tokens['unknown'].append(token)
            elif variables_count == 2 or \
                    ('=' in token
                     and
                     sy.simplify(token.split('=')[0]).free_symbols | function.free_symbols == {x}):
                # If it is an implicit function
                graph = MathFunction(token.strip(), function, 'implicit', list(function.free_symbols))
                self.tokens['implicit'].append(graph)
            elif variables_count <= 1:
                # If it is an explicit function
                graph = MathFunction(token.strip(), function, 'explicit', list(function.free_symbols))
                self.tokens['explicit'].append(graph)

        return self.tokens
