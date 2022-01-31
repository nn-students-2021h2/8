import json
import pathlib
import re

import sympy as sy
from sympy import SympifyError

from source.math.math_function import MathFunction
# This exception raise when sympy cannot draw a function plot
from source.math.parser import Parser, ParseError


def process_function(token: str):
    expr_parts = token.split('=')
    parts_count = len(expr_parts)
    try:
        if parts_count == 1:
            function = sy.simplify(expr_parts[0])
        elif parts_count == 2:
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

        return function
    except SympifyError as err:
        raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                         "Please, check your math formula.") from err


class CalculusParser(Parser):
    def __init__(self):
        super().__init__()
        self.action = ""
        self.function = None
        self.additional_params = []

    def make_latex(self, expression: list) -> str:
        result = ""
        pattern_set = self.action
        function = sy.latex(self.function.simplified_expr)
        symbols = list(map(sy.latex, self.function.symbols))
        first_result = sy.latex(expression[0])
        second_result = sy.latex(expression[1]) if len(expression) > 1 else None
        third_result = sy.latex(expression[2]) if len(expression) > 2 else None

        if pattern_set == "derivative":
            if len(self.additional_params):
                variables = self.additional_params[0].strip()
                variables = re.sub(" +", " ", variables)
                result = fr"Derivative\ of\ {function} by\ {variables}:\\{first_result}"
            else:
                result = fr"Derivative\ of\ {function}:\\{first_result}"

        elif pattern_set == "domain":
            result = fr"Domain\ of\ {function}:\\{first_result}"

        elif pattern_set == "range":
            result = fr"Range\ of\ {function}:\\{first_result}"

        elif pattern_set == "zeros":
            result = fr"Zeros\ of\ {function}:\\{first_result}"

        elif pattern_set == "axes_intersection":
            result = fr"Intersection\ with\ {symbols[0]}-axis:\\{symbols[1]} = {first_result}\\" \
                     fr"Intersection\ with\ {symbols[1]}-axis:\\{symbols[0]} = {second_result}"

        elif pattern_set == "periodicity":
            result = fr"Periodicity\ of\ {function}:\\{first_result}"

        elif pattern_set == "convexity":
            result = fr"Is\ {function} convex?\\{first_result}"

        elif pattern_set == "concavity":
            result = fr"Is\ {function} concave?\\{first_result}"

        elif pattern_set == "continuity":
            result = fr"Continuity interval of\ {function}:\\{first_result}"

        elif pattern_set == "vertical asymptotes":
            result = fr"Vertical\ asymptotes\ of\ {function}:\\{first_result}"

        elif pattern_set == "horizontal asymptotes":
            result = fr"Horizontal\ asymptotes\ of\ {function}:\\{first_result}"

        elif pattern_set == "slant asymptotes":
            result = fr"Slant\ asymptotes\ of\ {function}:\\{first_result}"

        elif pattern_set == "asymptotes":
            result = fr"Vertical\ asymptotes\ of\ {function}:\\{first_result}\\\\" \
                     fr"Horizontal\ asymptotes\ of\ {function}:\\{second_result}\\\\" \
                     fr"Slant\ asymptotes\ of\ {function}:\\{third_result}"

        elif pattern_set == "evenness":
            result = fr"Is\ {function}\ even?\\{first_result}"

        elif pattern_set == "oddness":
            result = fr"Is\ {function}\ odd?\\{first_result}"

        elif pattern_set == "maximum":
            result = fr"Max\ value\ of\ {function}:\\{first_result}"

        elif pattern_set == "minimum":
            result = fr"Min\ value\ of\ {function}:\\{first_result}"

        elif pattern_set == "stationary points":
            result = fr"Stationary\ points\ of\ {function}:\\{first_result}"

        return result

    def process_query(self) -> list:
        pattern_set = self.action
        m_func = self.function
        symbols = m_func.symbols

        result = []

        if pattern_set == "derivative":
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

        elif pattern_set == "domain":
            result.append(m_func.domain(symbols[0]))

        elif pattern_set == "range":
            result.append(m_func.frange(symbols[0]))

        elif pattern_set == "zeros":
            result.append(m_func.zeros())

        elif pattern_set == "axes_intersection":
            # If there is only one variable, then we should predict another one
            if len(symbols) == 1:
                first_variable = symbols[0]
                if str(first_variable) == "y":
                    symbols.append(sy.Symbol("x"))
                else:
                    symbols.append(sy.Symbol("y"))

            result.append(m_func.axis_intersection(symbols[0], symbols[1]))
            result.append(m_func.axis_intersection(symbols[1], symbols[0]))

        elif pattern_set == "periodicity":
            result.append(m_func.periodicity(symbols[0]))

        elif pattern_set == "convexity":
            result.append(m_func.convexity())

        elif pattern_set == "concavity":
            result.append(m_func.concavity())

        elif pattern_set == "continuity":
            result.append(m_func.continuity(symbols[0]))

        elif pattern_set == "vertical asymptotes":
            result.append(m_func.vertical_asymptotes(symbols[0]))

        elif pattern_set == "horizontal asymptotes":
            result.append(m_func.horizontal_asymptotes(symbols[0]))

        elif pattern_set == "slant asymptotes":
            result.append(m_func.slant_asymptotes(symbols[0]))

        elif pattern_set == "asymptotes":
            result.append(m_func.vertical_asymptotes(symbols[0]))
            result.append(m_func.horizontal_asymptotes(symbols[0]))
            result.append(m_func.slant_asymptotes(symbols[0]))

        elif pattern_set == "evenness":
            result.append(m_func.is_even(*symbols))

        elif pattern_set == "oddness":
            result.append(m_func.is_odd(*symbols))

        elif pattern_set == "maximum":
            result.append(m_func.maximum(symbols[0]))

        elif pattern_set == "minimum":
            result.append(m_func.minimum(symbols[0]))

        elif pattern_set == "stationary points":
            result.append(m_func.stationary_points(symbols[0]))

        return result

    def parse(self, query: str) -> bool:
        path = pathlib.Path(__file__).parent.resolve() / "patterns.json"
        file = open(path, "r")
        pattern_dict = json.load(file)
        re.match("^is[ ]+(.+)[ ]+odd[?]?$", "asdf")

        for pattern_set in pattern_dict:
            for pattern in pattern_dict[pattern_set]:
                p = re.compile(pattern)
                match = re.match(p, query)

                if match:
                    # Pattern parameters consist of last part of expression. Expression is a function to process
                    pattern_params = list(map(int, pattern_dict[pattern_set][pattern]))
                    expression = match.group(pattern_params[0])

                    # Extract the function from query and construct MathFunction
                    try:
                        function = process_function(expression)
                    except SympifyError as err:
                        raise ParseError(f"Mistake in function.\nYour input: {expression.strip()}\n"
                                         "Please, check your math formula.") from err
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

                    # Find the right pattern and get the result
                    return True

        file.close()
        return False
