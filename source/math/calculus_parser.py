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

    def _process_query(self, m_func, match, pattern_params, pattern_set, result, symbols):
        if pattern_set == "derivative":
            symbols = []

            # If it is a pattern with additional parameters (symbols, for example: diff x + y by x),
            # than extract variables to differentiate, else sympy will try to predict the variable
            if len(pattern_params) > 1:
                variables = match.group(pattern_params[1]).strip().replace(',', ' ')
                symbols = sy.symbols([*re.split("[ ]+", variables)])

                # Check if listed variables are correct
                for var in symbols:
                    if not str(var).isalpha():
                        raise ParseError(f"Variables can only contain letters\nIncorrect variable: '{var}'")

            result = fr"Derivative\ of {sy.latex(m_func.simplified_expr)}:\\{m_func.derivative(*symbols)}"

        elif pattern_set == "domain":
            result = fr"Domain\ of {sy.latex(m_func.simplified_expr)}:\\{sy.latex(m_func.domain(symbols[0]))}"

        elif pattern_set == "range":
            result = fr"Range\ of {sy.latex(m_func.simplified_expr)}:\\{sy.latex(m_func.frange(symbols[0]))}"

        elif pattern_set == "zeros":
            result = fr"Zeros\ of {sy.latex(m_func.simplified_expr)}:\\{sy.latex(m_func.zeros())}"

        elif pattern_set == "axes_intersection":
            # If there is only one variable, then we should predict another one
            if len(symbols) == 1:
                first_variable = symbols[0]
                if str(first_variable) == "y":
                    symbols.append(sy.Symbol("x"))
                else:
                    symbols.append(sy.Symbol("y"))

            first_intersection = sy.latex((m_func.axis_intersection(symbols[0], symbols[1])))
            result = fr"Intersection\ with {sy.latex(symbols[0])}-axis:\\" \
                     fr"{sy.latex(symbols[1])} = {first_intersection}\\"
            second_intersection = sy.latex((m_func.axis_intersection(symbols[1], symbols[0])))
            result += fr"Intersection\ with {sy.latex(symbols[1])}-axis:\\" \
                      fr"{sy.latex(symbols[0])} = {second_intersection}"

        elif pattern_set == "periodicity":
            result = fr"Periodicity\ of {m_func.simplified_expr}:\\" \
                     fr"{sy.latex(m_func.periodicity(symbols[0]))}"

        elif pattern_set == "convexity":
            result = fr"Is {sy.latex(m_func.simplified_expr)} convex?\\{sy.latex(m_func.convexity())}"

        elif pattern_set == "concavity":
            result = fr"Is {sy.latex(m_func.simplified_expr)} concave?\\{sy.latex(m_func.concavity())}"

        elif pattern_set == "continuity":
            result = fr"Continuity interval of {m_func.simplified_expr}:\\" \
                     fr"{sy.latex(m_func.continuity(symbols[0]))}"
        return result

    def parse(self, query: str) -> str:
        path = pathlib.Path(__file__).parent.resolve() / "patterns.json"
        file = open(path, "r")
        pattern_dict = json.load(file)

        result = ""

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

                    # Find the right pattern and get the result
                    return self._process_query(m_func, match, pattern_params, pattern_set, result, symbols)

        file.close()
        return result
