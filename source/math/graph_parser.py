"""
Parser for graph requests
"""
import json
import pathlib
import re

import sympy as sy
from sympy import SympifyError

from source.math.math_function import MathFunction, replace_incorrect_functions
from source.math.parser import Parser, STATEMENTS_LIMIT, ParseError


def _split_query(expr: str) -> list:
    # Replace some commas with '#' character to indicate parts to parse
    bracket_sequence = 0
    brackets = {
        '(': ')',
        '[': ']',
        '{': '}'
    }
    expr_lst = list(expr)
    for letter_index, letter in enumerate(expr_lst):
        if letter in brackets:
            bracket_sequence += 1
        elif letter in brackets.values():
            bracket_sequence -= 1

        # We don't want to replace commas in complex functions like root(x, 3)
        if bracket_sequence == 0 and letter in [',', ';', '\n']:
            expr_lst[letter_index] = '#'

        if (bracket_sequence < 0) or (bracket_sequence > 0 and letter_index == len(expr_lst) - 1):
            raise ParseError("Incorrect bracket sequence. Check your expression.")

    expr = "".join(expr_lst)
    parts = re.split('#', expr)
    return parts


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
        self.tokens = {'aspect ratio': [], 'domain': [], 'range': [], 'explicit': [], 'implicit': []}

    def _update_domain_range(self, match: re.Match, pattern_params: list, pattern_set: str, token: str):
        """
        Extract domain or range of the function and update tokens
        :param match: pattern from which we can get numbers
        :param pattern_params: list of groups of parameters in match
        :param pattern_set: class of query ("domain" or "range")
        :param token: considering part of query
        """
        try:
            left = float(match.group(pattern_params[0]))
            right = float(match.group(pattern_params[1]))
        except ValueError as err:
            raise ParseError(f"Mistake in function {pattern_set} parameters.\n"
                             f"Your input: {token.strip()}\n"
                             f"Please, check if numbers are correct.") from err
        if left >= right:
            raise ParseError(f"Mistake in function {pattern_set} parameters.\n"
                             f"Your input: {token.strip()}\n"
                             f"Left argument cannot be more or equal than right one: "
                             f"{left} >= {right}.")
        self.tokens[pattern_set] = [left, right]

    def _update_aspect_ratio(self, match: re.Match, pattern_params: list, pattern_set: str, token: str):
        """Check function above"""
        try:
            ratio = float(match.group(pattern_params[0]))
        except ValueError as err:
            raise ParseError(f"Mistake in aspect ratio.\n"
                             f"Your input: {token.strip()}\n"
                             f"Please, check if number is correct.") from err

        if ratio <= 0:
            raise ParseError(f"Mistake in aspect ratio.\n"
                             f"Your input: {token.strip()}\n"
                             f"Aspect ratio cannot be negative or equal to zero.")
        self.tokens[pattern_set] = [ratio]

    def _find_pattern(self, pattern_dict: dict, token: str, try_predict: bool) -> bool:
        """
        Tries to find suitable pattern for given token and apply it (change tokens)
        :param pattern_dict: dictionary of patterns
        :param token: part of user input
        :param try_predict: if there is a need to fix query
        :return: true if the pattern was found, false otherwise
        """
        for pattern_set in pattern_dict:
            for pattern in pattern_dict[pattern_set]["patterns"]:
                p = re.compile(pattern)

                # Match pattern if we don't want to predict the correct pattern
                match = None
                if not try_predict:
                    match = re.match(p, token)

                # If we want to find correct pattern again, we need to fix wrong words in query
                if try_predict and (fixed_query := self._fix_words(token, pattern_set, pattern_dict)):
                    match = re.match(p, fixed_query)

                if match:
                    # Pattern parameters consist of last part of expression. Expression is a function to process
                    pattern_params = list(map(int, pattern_dict[pattern_set]["patterns"][pattern]))

                    match pattern_set:
                        case "domain":
                            self._update_domain_range(match, pattern_params, pattern_set, token)
                        case "range":
                            self._update_domain_range(match, pattern_params, pattern_set, token)
                        case "aspect ratio":
                            self._update_aspect_ratio(match, pattern_params, pattern_set, token)

                    return True

        return False

    def _process_variables(self, function: sy.Function) -> sy.Function:
        """
        Replace all incorrect variables with correct (on 'x' and 'y')
        :param function: function to correct
        :return: corrected function
        """
        x, y = sy.symbols("x y")

        symbols = function.free_symbols

        # First check: expression contains x, a (replace a = y)
        if (x in symbols) and (y not in symbols) and len(var := list(symbols - {x})) == 1:
            self.push_warning(f"Variable '{var[0]}' is replaced by 'y'")
            return function.replace(var[0], y)

        # Second check: expression contains y, a (replace a = x)
        if (y in symbols) and (x not in symbols) and len(var := list(symbols - {y})) == 1:
            self.push_warning(f"Variable '{var[0]}' is replaced by 'x'")
            return function.replace(var[0], x)

        # Third check: expression contains a, b (replace a = x, b = y)
        if (x not in symbols) and (y not in symbols) and len(symbols) == 2:
            variables = list(symbols)
            self.push_warning(f"Variable '{variables[0]}' is replaced by 'y',\n"
                              f"variable '{variables[1]}' is replaced by 'x'")
            return function.replace(variables[0], y).replace(variables[1], x)

        # Fourth check: expression contains a (replace a = x)
        if (x not in symbols) and (y not in symbols) and len(var := list(symbols)) == 1:
            self.push_warning(f"Variable '{var[0]}' is replaced by 'x'")
            return function.replace(var[0], x)

        return function

    def _process_function(self, token: str) -> sy.Function:
        """
        Converting a string into a sympy function
        :param token: string to convert
        :return: sympy simplified function object
        """
        token = replace_incorrect_functions(token)
        expr_parts = token.split('=')
        parts_count = len(expr_parts)
        try:
            if parts_count == 1:
                function = sy.simplify(expr_parts[0])
            elif parts_count == 2:
                # If parsed result always true or false (e.g. it is not a function at all)
                result = sy.Eq(sy.simplify(expr_parts[0]), sy.simplify(expr_parts[1]))

                # Check if number of variables is less than 2
                if len(result.free_symbols) > 2:
                    raise ParseError(f"Incorrect expression: {token}\n"
                                     f"There are {len(result.free_symbols)} variables: "
                                     f"{', '.join(str(var) for var in result.free_symbols)}\n"
                                     f"You can use a maximum of 2 variables.")

                # If it is expressions like 1 = 1 or 1 = 0
                if result is sy.true or result is sy.false:
                    raise ParseError(f"Result of expression '{token}' is always {result}")

                # If expression like 'y = x', then discard left part, else construct expression "y - x = 0"
                # or if expression is not like 'y = y ** 2' (same variables at the both sides)
                vars_intersection = result.lhs.free_symbols & result.rhs.free_symbols
                if re.match("^y$", expr_parts[0].strip()) is not None and len(vars_intersection) == 0:
                    modified_expr = expr_parts[1]
                    function = sy.simplify(modified_expr)
                else:
                    modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"
                    function = sy.Eq(sy.simplify(modified_expr), 0)

            else:
                raise ParseError("Mistake in implicit function: Found more than 2 equals.\n"
                                 f"Your input: {token.strip()}\n"
                                 "Please, check your math formula")

            # Change variables
            function = self._process_variables(function)

            # Trying to convert implicit function into explicit (in order to optimize job)
            # We can't be sure if function can be converted in case several solutions for 'y'
            # solutions = sy.solve(function, y)
            # if len(solutions) == 1:
            #     function = solutions[0]

            return function
        except (SympifyError, TypeError, ValueError) as err:
            raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                             "Please, check your math formula.") from err

    def parse(self, expr: str):
        """
        This method get string and tries to parse it in several groups (see 'tokens' variable)

        Parameters:
        :param expr: user input string to parse
        :return: true on successfully found patterns, false otherwise
        """
        parts = _split_query(expr)

        if len(parts) >= STATEMENTS_LIMIT:
            raise ParseError(f"Too many arguments. The limit is {STATEMENTS_LIMIT} statements.")

        path = pathlib.Path(__file__).parent.resolve() / "graph_patterns.json"
        with open(path, "r", encoding="utf-8") as file:
            pattern_dict = json.load(file)

        for token in parts:
            token = token.strip()

            # Check if expression matches any pattern
            if self._find_pattern(pattern_dict, token, False):
                continue

            # If it is a function
            try:
                function = self._process_function(token)
            except ParseError as err:
                # If we don't found a pattern, and it is not a function, then try to fix words
                if self._find_pattern(pattern_dict, token, True):
                    continue

                raise err

            # Next complex check finds expressions like "x = 1".
            # They should be implicit because of sympy specifics
            is_x_equal_num = self.is_x_equal_num_expression(token)

            # Update tokens list
            variables_count = len(function.free_symbols)

            # If there are two variables or expression like 'x = 1' or equation 'something = 0'
            if variables_count == 2 or is_x_equal_num or isinstance(function, sy.Equality):
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
