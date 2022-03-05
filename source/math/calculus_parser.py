"""
Parser for function analysis requests
"""
import json
import pathlib
import re

import sympy as sy
from sympy import SympifyError

from source.extras.utilities import run_asynchronously
from source.math.math_function import MathFunction, replace_incorrect_functions
from source.math.parser import Parser, ParseError


def _process_function(token: str) -> sy.Function:
    """
    Converting a string into a sympy function
    :param token: string to convert
    :return: sympy simplified function object
    """
    # Fix all incorrect functions in string representation of function
    token = replace_incorrect_functions(token)
    expr_parts = token.split('=')
    parts_count = len(expr_parts)
    try:
        if parts_count == 1:
            function = sy.simplify(expr_parts[0])
        elif parts_count == 2:
            # If expression like 'y = x', then discard left part, else construct expression "y - x = 0"
            result = sy.Eq(sy.simplify(expr_parts[0]), sy.simplify(expr_parts[1]))
            vars_intersection = result.lhs.free_symbols & result.rhs.free_symbols
            if re.match("^y$", expr_parts[0].strip()) is not None and len(vars_intersection) == 0:
                modified_expr = expr_parts[1]
            else:
                modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"

            function = sy.simplify(modified_expr)
        else:
            raise ParseError("Mistake in implicit function: found more than 2 equals.\n"
                             f"Your input: {token.strip()}\n"
                             "Please, check your math formula.")

        return function
    except (SympifyError, TypeError, ValueError) as err:
        raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                         "Please, check your math formula.") from err


class CalculusParser(Parser):
    """
    This class is used to parse user input, which is a function analysis request.

    Attributes:
    :param action: a pattern class (string) that written in analyse_patterns.json (e.g. derivative, zeros, asymptotes)
    :param function: MathFunction object representing user function to handle
    :param additional_params: a list of additional information that can be used in calculating the result
    """

    def __init__(self, action="", function=None, additional_params=None):
        super().__init__()
        if additional_params is None:
            additional_params = []
        self.action = action
        self.function = function
        self.additional_params = additional_params

    def _find_pattern(self, query: str, pattern_dict: dict, try_predict: bool) -> bool:
        """
        Tries to find pattern matching the given query
        :param query: user input
        :param pattern_dict: a dictionary of patterns
        :param try_predict: if there is a need to correct the query and try to find pattern again
        :return: true if pattern was found, otherwise false
        """
        for pattern_set in pattern_dict:
            for pattern in pattern_dict[pattern_set]["patterns"]:
                p = re.compile(pattern)

                # Match pattern if we don't want to predict the correct pattern
                match = None
                if not try_predict:
                    match = re.match(p, query)

                # If we want to find correct pattern again, we need to fix wrong words in query
                if try_predict and (fixed_query := self._fix_words(query, pattern_set, pattern_dict)):
                    match = re.match(p, fixed_query)

                if match:
                    # Pattern parameters consist of last part of expression. Expression is a function to process
                    pattern_params = list(map(int, pattern_dict[pattern_set]["patterns"][pattern]))
                    expression = match.group(pattern_params[0])

                    # Extract the function from query and construct MathFunction
                    function = _process_function(expression)
                    m_func = MathFunction(expression, function)
                    symbols = sorted(list(m_func.simplified_expr.free_symbols), key=lambda x: str(x))

                    # Check if listed variables are correct
                    for var in symbols:
                        if not str(var).isalpha():
                            raise ParseError(f"Variables can only contain letters\nIncorrect variable: '{var}'")

                    # If there is no variables, then we can't get the answer. In order to not getting errors,
                    # we can append fictitious variable 'x'
                    if len(symbols) == 0:
                        symbols.append(sy.Symbol("x"))
                    m_func.symbols = symbols

                    # Set the parser variables
                    self.action = pattern_set
                    self.function = m_func
                    self.additional_params = [match.group(param) for param in pattern_params[1:]]

                    return True

                self.clear_warnings()

        return False

    def make_latex(self, expression: list) -> str:
        """
        Converts the given argument into LaTeX format according to the parser's pattern set
        :param expression: list of expressions that should be represented in LaTeX format
        :return: LaTeX representation (string). If is can't find pattern set, then returns empty string
        """
        result = ""
        pattern_set = self.action
        function = sy.latex(self.function.simplified_expr)
        symbols = list(map(sy.latex, self.function.symbols))
        first_result = sy.latex(expression[0])
        second_result = sy.latex(expression[1]) if len(expression) > 1 else None
        third_result = sy.latex(expression[2]) if len(expression) > 2 else None

        match pattern_set:
            case "derivative":
                if len(self.additional_params) > 0:
                    variables = self.additional_params[0].strip()
                    variables = re.sub(" +", " ", variables)
                    result = fr"Derivative\ of\ {function}\ by\ {variables}:\\{first_result}"
                else:
                    result = fr"Derivative\ of\ {function}:\\{first_result}"

            case "domain":
                result = fr"Domain\ of\ {function}:\\{first_result}"

            case "range":
                result = fr"Range\ of\ {function}:\\{first_result}"

            case "zeros":
                result = fr"Zeros\ of\ {function}:\\{first_result}"

            case "axes_intersection":
                result = fr"For\ function\ {function}:\\" \
                         fr"Intersection\ with\ {symbols[0]}-axis:\\{symbols[0]} = {first_result}\\" \
                         fr"Intersection\ with\ {symbols[1]}-axis:\\{symbols[1]} = {second_result}"

            case "periodicity":
                result = fr"Periodicity\ of\ {function}:\\{first_result}"

            case "convexity":
                result = fr"Is\ {function}\ convex?\\{first_result}"

            case "concavity":
                result = fr"Is\ {function}\ concave?\\{first_result}"

            case "continuity":
                result = fr"Continuity\ interval\ of\ {function}:\\{first_result}"

            case "vertical asymptotes":
                result = fr"Vertical\ asymptotes\ of\ {function}:\\{first_result}"

            case "horizontal asymptotes":
                result = fr"Horizontal\ asymptotes\ of\ {function}:\\{first_result}"

            case "slant asymptotes":
                result = fr"Slant\ asymptotes\ of\ {function}:\\{first_result}"

            case "asymptotes":
                result = fr"Vertical\ asymptotes\ of\ {function}:\\{first_result}\\\\" \
                         fr"Horizontal\ asymptotes\ of\ {function}:\\{second_result}\\\\" \
                         fr"Slant\ asymptotes\ of\ {function}:\\{third_result}"

            case "evenness":
                result = fr"Is\ {function}\ even?\\{first_result}"

            case "oddness":
                result = fr"Is\ {function}\ odd?\\{first_result}"

            case "maximum":
                result = fr"Max\ value\ of\ {function}:\\{first_result}"

            case "minimum":
                result = fr"Min\ value\ of\ {function}:\\{first_result}"

            case "stationary points":
                result = fr"Stationary\ points\ of\ {function}:\\{first_result}"

        return result

    @run_asynchronously
    def process_query(self) -> list:
        """
        Tries to calculate the requested function
        :return: list of results
        """
        m_func = self.function
        symbols = m_func.symbols

        result = []

        match self.action:
            case "derivative":
                symbols = []

                # If it is a pattern with additional parameters (symbols, for example: diff x + y by x),
                # than extract variables to differentiate, else sympy will try to predict the variable
                if len(self.additional_params) > 0:
                    variables = self.additional_params[0].strip().replace(',', ' ')
                    symbols = sy.symbols([*re.split("[ ]+", variables)])

                    # Check if listed variables are correct
                    for var in symbols:
                        if not str(var).isalpha():
                            raise ParseError(f"Variables can only contain letters\nIncorrect variable: '{var}'")

                result.append(m_func.derivative(*symbols))

            case "domain":
                result.append(m_func.domain(symbols[0]))

            case "range":
                result.append(m_func.frange(symbols[0]))

            case "zeros":
                result.append(m_func.zeros())

            case "axes_intersection":
                # If there is only one variable, then we should predict another one
                if len(symbols) == 1:
                    first_variable = symbols[0]
                    if str(first_variable) == "y":
                        symbols.append(sy.Symbol("x"))
                    else:
                        symbols.append(sy.Symbol("y"))

                result.append(m_func.axis_intersection(symbols[0], symbols[1]))
                result.append(m_func.axis_intersection(symbols[1], symbols[0]))

            case "periodicity":
                result.append(m_func.periodicity(symbols[0]))

            case "convexity":
                result.append(m_func.convexity(symbols[0]))

            case "concavity":
                result.append(m_func.concavity(symbols[0]))

            case "continuity":
                result.append(m_func.continuity(symbols[0]))

            case "vertical asymptotes":
                result.append(m_func.vertical_asymptotes(symbols[0]))

            case "horizontal asymptotes":
                result.append(m_func.horizontal_asymptotes(symbols[0]))

            case "slant asymptotes":
                result.append(m_func.slant_asymptotes(symbols[0]))

            case "asymptotes":
                result.append(m_func.vertical_asymptotes(symbols[0]))
                result.append(m_func.horizontal_asymptotes(symbols[0]))
                result.append(m_func.slant_asymptotes(symbols[0]))

            case "evenness":
                result.append(m_func.is_even(*symbols))

            case "oddness":
                result.append(m_func.is_odd(*symbols))

            case "maximum":
                result.append(m_func.maximum(symbols[0]))

            case "minimum":
                result.append(m_func.minimum(symbols[0]))

            case "stationary points":
                result.append(m_func.stationary_points(symbols[0]))

        return result

    @run_asynchronously
    def parse(self, query: str) -> bool:
        """
        Fills in class attributes based on the user request
        Correlates user input with patterns defined in analyse_patterns.json
        Extract function and additional parameters from input query
        :param query: user input, string (e.g. diff of x**2 by x)
        :return: true on successfully found pattern, false otherwise
        """
        path = pathlib.Path(__file__).parent.resolve() / "analyse_patterns.json"
        with open(path, "r", encoding="utf-8") as file:
            pattern_dict = json.load(file)

        # Check if input match any pattern
        is_pattern_found = self._find_pattern(query, pattern_dict, False)
        if is_pattern_found:
            return True

        # If none of patterns were satisfied, then we can try to correct input and match the patterns again
        return self._find_pattern(query, pattern_dict, True)
