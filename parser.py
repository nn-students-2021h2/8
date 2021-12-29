"""
User input parser module
"""

import sympy as sy
from sympy import SympifyError

from math_function import MathFunction


# This exception raise when sympy cannot draw a function plot


class ParseError(Exception):
    """This exception will be thrown when something went wrong while parsing"""


class Parser:
    """
    This class represents parser for user input. Now, it parses expressions like:
    x**2 + y^2, x, y = a, x = 1, from -12 to -2

    If parse input into dictionary 'tokens'
    """

    def __init__(self):
        self.tokens = {'range': [], 'explicit': [], 'implicit': [], 'unknown': []}
        self.last_warning = ''

    def pop_last_warning(self) -> str:
        """
        Delete last_warning and return its value
        :return: last warning as string
        """
        warning, self.last_warning = self.last_warning, ''
        return warning

    def _process_range(self, token: str) -> bool:
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

    def _process_variables(self, token: str, function):
        x, y = sy.symbols("x y")

        # First check: expression contains more than three variables (a, b, c)
        symbols = function.free_symbols
        if len(symbols) >= 3:
            raise ParseError(f"Incorrect expression: {token}\n"
                             f"There are {len(symbols)} variables: "
                             f"{', '.join(str(var) for var in symbols)}\n"
                             f"You can use a maximum of 2 variables.")

        # Second check: expression contains x, a (replace a = y)
        if (x in symbols) and (y not in symbols) and len(var := list(symbols - {x})) == 1:
            self.last_warning = f"Variable '{var[0]}' is replaced by 'y'"
            return function.replace(var[0], y)

        # Third check: expression contains y, a (replace a = x)
        if (y in symbols) and (x not in symbols) and len(var := list(symbols - {y})) == 1:
            self.last_warning = f"Variable '{var[0]}' is replaced by 'x'"
            return function.replace(var[0], x)

        # Fourth check: expression contains a, b (replace a = x, b = y)
        if (x not in symbols) and (y not in symbols) and len(symbols) == 2:
            variables = list(symbols)
            self.last_warning = f"Variable '{variables[0]}' is replaced by 'y',\n" \
                                f"variable '{variables[1]}' is replaced by 'x'"
            return function.replace(variables[0], y).replace(variables[1], x)

        # Fifth check: expression contains a (replace a = x)
        if (x not in symbols) and (y not in symbols) and len(var := list(symbols)) == 1:
            self.last_warning = f"Variable '{var[0]}' is replaced by 'x'"
            return function.replace(var[0], x)

        return function

    def _process_function(self, token: str):
        expr_parts = token.split('=')
        parts_count = len(expr_parts)
        x, y = sy.symbols("x y")
        try:
            if parts_count == 1:
                function = sy.simplify(expr_parts[0])
                function = self._process_variables(token, function)
            elif parts_count == 2:
                modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"
                function = sy.simplify(modified_expr)
                function = self._process_variables(token, function)
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
                if self._process_range(token):
                    continue
            except ParseError as err:
                raise err

            # If it is a function
            try:
                function = self._process_function(token)
            except ParseError as err:
                raise err

            # Update tokens list
            variables_count = len(function.free_symbols)
            if variables_count == 2 or \
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
            else:
                # If it is an unknown expression
                self.tokens['unknown'].append(token)

        return self.tokens
