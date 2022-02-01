"""
Parser for graph requests
"""
import re

import sympy as sy
from sympy import SympifyError

from source.math.math_function import MathFunction
from source.math.parser import Parser, STATEMENTS_LIMIT, ParseError


class GraphParser(Parser):
    """
    This class represents parser for user input. Now, it parses expressions like:
    x**2 + y^2, x, y = a, x = 1, from -12 to -2

    User input is parsed in 'tokens' dictionary by several groups:
    - range : function domain
    - explicit : explicit functions
    - implicit : implicit functions (or not functions) that can't be converted into explicit
    """

    def __init__(self):
        super().__init__()
        self.tokens = {'range': [], 'explicit': [], 'implicit': []}

    def _process_range(self, token: str) -> bool:
        # if re.match(r"^from[ ]+[-+]?(\d)+[.]?(\d)+[ ]+to[ ]+[-+]?\d+[.]?\d+$", token.strip()):
        if re.match("^from[ ]+(.+)[ ]+to[ ]+(.+)$", token.strip()):
            definition_area = token.split()
            try:
                left = float(definition_area[1])
                right = float(definition_area[3])
            except ValueError as err:
                raise ParseError(f"Mistake in function range parameters.\n"
                                 f"Your input: {token.strip()}\n"
                                 f"Please, check your \"from _ to _\" statement.") from err

            if left >= right:
                raise ParseError(f"Mistake in function range parameters.\n"
                                 f"Your input: {token.strip()}\n"
                                 f"Left argument cannot be more or equal than right one: {left} >= {right}.")

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
            self.push_warning(f"Variable '{var[0]}' is replaced by 'y'")
            return function.replace(var[0], y)

        # Third check: expression contains y, a (replace a = x)
        if (y in symbols) and (x not in symbols) and len(var := list(symbols - {y})) == 1:
            self.push_warning(f"Variable '{var[0]}' is replaced by 'x'")
            return function.replace(var[0], x)

        # Fourth check: expression contains a, b (replace a = x, b = y)
        if (x not in symbols) and (y not in symbols) and len(symbols) == 2:
            variables = list(symbols)
            self.push_warning(f"Variable '{variables[0]}' is replaced by 'y',\n"
                              f"variable '{variables[1]}' is replaced by 'x'")
            return function.replace(variables[0], y).replace(variables[1], x)

        # Fifth check: expression contains a (replace a = x)
        if (x not in symbols) and (y not in symbols) and len(var := list(symbols)) == 1:
            self.push_warning(f"Variable '{var[0]}' is replaced by 'x'")
            return function.replace(var[0], x)

        return function

    def _process_function(self, token: str):
        expr_parts = token.split('=')
        parts_count = len(expr_parts)
        try:
            if parts_count == 1:
                function = sy.simplify(expr_parts[0])
            elif parts_count == 2:
                # If parsed result always true or false (e.g. it is not a function at all)
                result = sy.Eq(sy.simplify(expr_parts[0]), sy.simplify(expr_parts[1]))
                if result is sy.true or result is sy.false:
                    raise ParseError(f"Result of expression '{token}' is always {result}")

                # If expression like 'y = x', then discard left part, else construct expression "y - x = 0"
                if re.match("^y$", expr_parts[0].strip()) is not None:
                    modified_expr = expr_parts[1]
                else:
                    modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"

                function = sy.simplify(modified_expr)
            else:
                raise ParseError("Mistake in implicit function: Found more than 2 equals.\n"
                                 f"Your input: {token.strip()}\n"
                                 "Please, check your math formula")

            # Change variables
            function = self._process_variables(token, function)

            # Trying to convert implicit function into explicit (in order to optimize job)
            # We can't be sure if function can be converted in case several solutions for 'y'
            # solutions = sy.solve(function, y)
            # if len(solutions) == 1:
            #     function = solutions[0]

            return function
        except (SympifyError, TypeError) as err:
            raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                             "Please, check your math formula.") from err

    def parse(self, expr: str):
        """
        This method get string and tries to parse it in several groups (see 'tokens' variable)

        Parameters:
        :param expr: user input string to parse
        :return: parsed user input in the form of dictionary 'tokens'
        """
        parts = re.split("[,;\n]", expr)

        if len(parts) >= STATEMENTS_LIMIT:
            raise ParseError(f"Too many arguments. The limit is {STATEMENTS_LIMIT} statements.")

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

            # Next complex checking finds expressions like "x = 1".
            # They should be implicit because of sympy specifics
            is_x_equal_num = self.is_x_equal_num_expression(token)

            # Update tokens list
            variables_count = len(function.free_symbols)

            if variables_count == 2 or is_x_equal_num:
                # If it is an implicit function
                graph = MathFunction(token.strip(), function, 'implicit', list(function.free_symbols))
                self.tokens['implicit'].append(graph)
            elif variables_count <= 1:
                # If it is an explicit function
                graph = MathFunction(token.strip(), function, 'explicit', list(function.free_symbols))
                self.tokens['explicit'].append(graph)
            else:
                # If it is an unknown expression
                raise ParseError(f"Cannot resolve statement: {token}")

        return self.tokens
