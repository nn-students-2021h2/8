"""
Parser for graph requests
"""
import multiprocessing
import re
from tokenize import TokenError

import sympy as sy
from sympy import SympifyError
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, standard_transformations

from source.conf import Config
from source.extras.translation import _
from source.extras.utilities import run_asynchronously
from source.math.math_function import MathFunction, replace_incorrect_functions
from source.math.parser import Parser, ParseError


def _split_query(expr: str, lang: str = "en") -> list:
    """
    Tries to split a query string correctly.
    Calculates correct bracket sequence and marks necessary commas as delimiters (by replacing it with '#')
    :param lang:
    :param expr: user input
    :return: list of expression parts (tokens)
    """
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
            raise ParseError(_("Incorrect bracket sequence. Check your expression.", locale=lang))

    expr = "".join(expr_lst)
    parts = re.split('#', expr)
    return parts


class GraphParser(Parser):
    """
    This class represents parser for user input. Now, it parses expressions like:
    x**2 + y^2, x, y = a, x = 1, x from -12 to -2, ratio=2

    User input is parsed in 'tokens' dictionary by several groups:
    - aspect ratio : aspect ratio of the final picture (e.g. [2])
    - domain : function domain, i.e. x-limit (e.g. [-10, 10])
    - range : function range, i.e. y-limit (e.g. [-10, 10])
    - explicit : explicit functions (e.g. y = x**2)
    - implicit : implicit functions (or not functions) that can't be converted into explicit (e.g. y**2 + x**2 = 4)
    """

    # Limitation on the number of requested functions
    FUNCTIONS_LIMIT = 10

    def __init__(self):
        super().__init__()
        self.tokens = {'aspect ratio': [], 'domain': [], 'range': [], 'explicit': [], 'implicit': []}

    def _update_domain_range(self, match: re.Match, pattern_params: list, pattern_set: str, token: str,
                             lang: str = "en"):
        """
        Extract domain or range of the function and update tokens
        :param lang:
        :param match: pattern from which we can get numbers
        :param pattern_params: list of groups of parameters in match
        :param pattern_set: class of query ("domain" or "range")
        :param token: considering part of query
        """
        try:
            left = float(match.group(pattern_params[0]))
            right = float(match.group(pattern_params[1]))
        except ValueError as err:
            raise ParseError(_("Mistake in function {} parameters.\n"
                               "Your input: {}\n"
                               "Please, check if numbers are correct.",
                               locale=lang).format(pattern_set, token.strip())) from err
        if left >= right:
            raise ParseError(_("Mistake in function {} parameters.\n"
                               "Your input: {}\n"
                               "Left argument cannot be more or equal than right one: "
                               "{} >= {}.", locale=lang).format(pattern_set, token.strip(), left, right))
        self.tokens[pattern_set] = [left, right]

    def _update_aspect_ratio(self, match: re.Match, pattern_params: list, pattern_set: str, token: str,
                             lang: str = "en"):
        """Check function above
        :param lang:
        """
        try:
            ratio = float(match.group(pattern_params[0]))
        except ValueError as err:
            raise ParseError(_("Mistake in aspect ratio.\n"
                               "Your input: {}\n"
                               "Please, check if number is correct.", locale=lang).format(token.strip())) from err

        if ratio <= 0:
            raise ParseError(_("Mistake in aspect ratio.\n"
                               "Your input: {}\n"
                               "Aspect ratio cannot be negative or equal to zero.", locale=lang).format(token.strip()))
        self.tokens[pattern_set] = [ratio]

    def _find_pattern(self, pattern_dict: dict, token: str, try_predict: bool, lang: str = "en") -> bool:
        """
        Tries to find suitable pattern for given token and apply it (change tokens)
        :param lang:
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
                if try_predict and (fixed_query := self._fix_words(token, pattern_set, pattern_dict, lang)):
                    match = re.match(p, fixed_query)

                if match:
                    # Pattern parameters consist of last part of expression. Expression is a function to process
                    pattern_params = list(map(int, pattern_dict[pattern_set]["patterns"][pattern]))

                    match pattern_set:
                        case "domain":
                            self._update_domain_range(match, pattern_params, pattern_set, token, lang)
                        case "range":
                            self._update_domain_range(match, pattern_params, pattern_set, token, lang)
                        case "aspect ratio":
                            self._update_aspect_ratio(match, pattern_params, pattern_set, token, lang)

                    return True

        return False

    def _process_variables(self, function: sy.Function, lang: str = "en") -> sy.Function:
        """
        Replace all incorrect variables with correct (on 'x' and 'y')
        :param lang:
        :param function: function to correct
        :return: corrected function
        """
        x, y = sy.symbols("x y")

        symbols = function.free_symbols

        # First check: expression contains x, a (replace a = y)
        if (x in symbols) and (y not in symbols) and len(var := list(symbols - {x})) == 1:
            self.push_warning(_("Variable '{}' is replaced by 'y'", locale=lang).format(var[0]))
            return function.replace(var[0], y)

        # Second check: expression contains y, a (replace a = x)
        if (y in symbols) and (x not in symbols) and len(var := list(symbols - {y})) == 1:
            self.push_warning(_("Variable '{}' is replaced by 'x'", locale=lang).format(var[0]))
            return function.replace(var[0], x)

        # Third check: expression contains a, b (replace a = x, b = y)
        if (x not in symbols) and (y not in symbols) and len(symbols) == 2:
            variables = list(symbols)
            self.push_warning(_("Variable '{}' is replaced by 'y',\n"
                                "variable '{}' is replaced by 'x'", locale=lang).format(variables[0], variables[1]))
            return function.replace(variables[0], y).replace(variables[1], x)

        # Fourth check: expression contains a (replace a = x)
        if (x not in symbols) and (y not in symbols) and len(var := list(symbols)) == 1:
            self.push_warning(_("Variable '{}' is replaced by 'x'", locale=lang).format(var[0]))
            return function.replace(var[0], x)

        return function

    def _process_function(self, token: str, lang: str = "en", q=None) -> None:
        """
        Converting a string into a sympy function
        :param lang:
        :param token: string to convert
        :return: sympy simplified function object
        """
        token = replace_incorrect_functions(token)
        expr_parts = token.split('=')
        parts_count = len(expr_parts)
        rules = standard_transformations + (implicit_multiplication_application, convert_xor)
        try:
            if parts_count == 1:
                function = sy.parse_expr(expr_parts[0], transformations=rules)

                # If there is only 'y' variable, then we can't understand what we should draw, because it is impossible
                # to change axes in plot in our case
                if function.free_symbols == {sy.Symbol('y')}:
                    q.put(ParseError(_("Incorrect expression: {}\n"
                                       "There is only 'y' variable. It's f(y) or f(x) = 0?\n"
                                       "Please, use 'x' instead of single 'y' variable for f(x) plot.",
                                       locale=lang).format(token)))
                    return
            elif parts_count == 2:
                # If parsed result always true or false (e.g. it is not a function at all)
                result = sy.Eq(sy.parse_expr(expr_parts[0], transformations=rules),
                               sy.parse_expr(expr_parts[1], transformations=rules))

                # Check if number of variables is less than 2
                if len(result.free_symbols) > 2:
                    variables = ', '.join(str(var) for var in result.free_symbols)
                    q.put(ParseError(_("Incorrect expression: {}\nThere are {} variables: {}\n"
                                       "You can use a maximum of 2 variables.",
                                       locale=lang).format(token,
                                                           len(result.free_symbols),
                                                           variables)))
                    return

                # If it is expressions like 1 = 1 or 1 = 0
                if result is sy.true or result is sy.false:
                    raise ParseError(_("Result of expression '{}' is always {}", locale=lang).format(token, result))

                # If expression like 'y = x', then discard left part, else construct expression "y - x = 0"
                # or if expression is not like 'y = y ** 2' (same variables at the both sides)
                vars_intersection = result.lhs.free_symbols & result.rhs.free_symbols
                if re.match("^y$", expr_parts[0].strip()) is not None and len(vars_intersection) == 0:
                    modified_expr = expr_parts[1]
                    function = sy.parse_expr(modified_expr, transformations=rules)
                else:
                    modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"
                    function = sy.Eq(sy.parse_expr(modified_expr, transformations=rules), 0)

            else:
                q.put(ParseError(_("Mistake in implicit function: found more than 1 equal sign.\n"
                                   "Your input: {}\n"
                                   "Please, check your math formula", locale=lang).format(token.strip())))
                return

            # Change variables
            function = self._process_variables(function, lang)
        except (SympifyError, TypeError, ValueError, AttributeError, TokenError):
            q.put(ParseError(_("Mistake in expression.\nYour input: {}\n"
                               "Please, check your math formula.", locale=lang).format(token.strip())))
            return
        except SyntaxError:
            q.put(ParseError(_("Couldn't make out the expression.\nYour input: {}\nTry using a stricter syntax, "
                               "such as placing '*' (multiplication) signs and parentheses.",
                               locale=lang).format(token.strip())))
            return

        # Check function length
        if len(str(function)) > Parser.FUNCTION_LENGTH_LIMIT:
            q.put(ParseError(_("One of the functions is too long.\nYour input: {}\nSorry for this limitation.",
                               locale=lang).format(str(token))))
            return

        q.put(function)

    @run_asynchronously
    def parse(self, query: str, lang: str = "en"):
        """
        This method get string and tries to parse it in several groups (see 'tokens' variable)

        Parameters:
        :param lang:
        :param query: user input string to parse
        :return: true on successfully found patterns, false otherwise
        """
        pattern_dict = Config.graph_patterns

        parts = _split_query(query, lang)

        for token in parts:
            token = token.strip()

            # Check if expression matches any pattern
            if self._find_pattern(pattern_dict, token, False, lang):
                continue

            # If it is a function
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=self._process_function, args=(token, lang, q))
            p.start()
            p.join(5)
            if p.is_alive():
                p.terminate()
                return None
            function = q.get()
            if isinstance(function, Exception):
                # If we don't found a pattern, and it is not a function, then try to fix words
                if self._find_pattern(pattern_dict, token, True, lang):
                    continue

                raise function

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
                raise ParseError(_("Cannot resolve a statement: {}", locale=lang).format(token))

        if (functions_count := len(self.tokens["explicit"]) + len(self.tokens["implicit"])) > self.FUNCTIONS_LIMIT:
            raise ParseError(_("Too many functions requested ({}). "
                               "The limit is {} functions.", locale=lang).format(functions_count, self.FUNCTIONS_LIMIT))

        return True
