"""
Parser for function analysis requests
"""
import multiprocessing
import re
from tokenize import TokenError

import sympy as sy
from sympy import SympifyError
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor

from source.conf import Config
from source.extras.translation import _
from source.extras.utilities import run_asynchronously
from source.math.math_function import MathFunction, replace_incorrect_functions
from source.math.parser import Parser, ParseError


def _process_function(token: str, lang: str = "en", q: multiprocessing.Queue = None) -> None:
    """
    Converting a string into a sympy function
    :param lang:
    :param token: string to convert
    :return: sympy simplified function object
    """
    # Fix all incorrect functions in string representation of function
    token = replace_incorrect_functions(token)
    expr_parts = token.split('=')
    parts_count = len(expr_parts)
    rules = standard_transformations + (implicit_multiplication_application, convert_xor)
    try:
        if parts_count == 1:
            function = sy.parse_expr(expr_parts[0], transformations=rules)
        elif parts_count == 2:
            # If expression like 'y = x', then discard left part, else construct expression "y - x = 0"
            result = sy.Eq(sy.parse_expr(expr_parts[0], transformations=rules),
                           sy.parse_expr(expr_parts[1], transformations=rules))
            vars_intersection = result.lhs.free_symbols & result.rhs.free_symbols
            if re.match("^y$", expr_parts[0].strip()) is not None and len(vars_intersection) == 0:
                modified_expr = expr_parts[1]
            else:
                modified_expr = f"{expr_parts[0]} - ({expr_parts[1]})"

            function = sy.parse_expr(modified_expr, transformations=rules)
        else:
            q.put(ParseError(_("Mistake in implicit function: found more than 1 equal sign.\n"
                               "Your input: {}\n"
                               "Please, check your math formula.", locale=lang).format(token.strip())))
            return


    except (SympifyError, TypeError, ValueError, AttributeError, TokenError):
        q.put(ParseError(_("Mistake in expression.\nYour input: {}\n"
                           "Please, check your math formula.", locale=lang).format(token.strip())))
        return

    except SyntaxError:
        q.put(ParseError(_("Couldn't make out the expression.\nYour input: {}\nTry using a stricter syntax, "
                           "such as placing '*' (multiplication) signs and parentheses.",
                           locale=lang).format(token.strip())))
        return

    q.put(function)


class CalculusParser(Parser):
    """
    This class is used to parse user input, which is a function analysis request.

    Attributes:
    :param action: a pattern class (string) that written in analyse_patterns.json (e.g. derivative, zeros, asymptotes)
    :param function: MathFunction object representing user function to handle
    :param additional_params: a list of additional information that can be used in calculating the result
    """

    def __init__(self, action: str = "", function: MathFunction = None, additional_params: list = None):
        super().__init__()
        if additional_params is None:
            additional_params = []
        self.action = action
        self.function = function
        self.additional_params = additional_params

    def _find_pattern(self, query: str, pattern_dict: dict, try_predict: bool, lang: str = "en") -> (bool | None):
        """
        Tries to find pattern matching the given query
        :param lang:
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
                if try_predict and (fixed_query := self._fix_words(query, pattern_set, pattern_dict, lang)):
                    match = re.match(p, fixed_query)

                if match:
                    # Pattern parameters consist of last part of expression. Expression is a function to process
                    pattern_params = list(map(int, pattern_dict[pattern_set]["patterns"][pattern]))
                    expression = match.group(pattern_params[0])

                    # Extract the function from query and construct MathFunction
                    q = multiprocessing.Queue()
                    p = multiprocessing.Process(target=_process_function, args=(expression, lang, q))
                    p.start()
                    p.join(5)
                    if p.is_alive():
                        p.terminate()
                        return None
                    function = q.get()
                    if isinstance(function, Exception):
                        raise function

                    # function = _process_function(expression, lang)
                    m_func = MathFunction(expression, function)
                    symbols = sorted(list(m_func.simplified_expr.free_symbols), key=lambda x: str(x))

                    # Check if listed variables are correct
                    for var in symbols:
                        if not str(var).isalpha() or not str(var).isascii():
                            raise ParseError(_("Variables can only contain latin letters\nIncorrect variable: '{}'",
                                               locale=lang).format(var))

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
        pattern_set = self.action
        function = sy.latex(self.function.simplified_expr)
        symbols = list(map(sy.latex, self.function.symbols))
        first_result = sy.latex(expression[0])
        second_result = sy.latex(expression[1]) if len(expression) > 1 else None
        third_result = sy.latex(expression[2]) if len(expression) > 2 else None

        # Aliases
        NL = r"\\"  # New Line
        NLC = r":\\"  # New Line with Colon
        SPACE = r"\ "  # Space in LaTeX format
        __ = lambda s: sy.latex(_(s))  # Translate and make latex

        match pattern_set:
            case "derivative":
                if len(self.additional_params) > 0:
                    variables = self.additional_params[0].strip()
                    variables = re.sub(" +", " ", variables)
                    result = SPACE.join(
                        [__("Derivative"), __("of"), function, __("by"), variables]
                    ) + NLC + first_result
                else:
                    result = SPACE.join(
                        [__("Derivative"), __("of"), function]
                    ) + NLC + first_result

            case "domain":
                result = SPACE.join(
                    [__("Domain"), __("of"), function]
                ) + NLC + first_result

            case "range":
                result = SPACE.join(
                    [__("Range"), __("of"), function]
                ) + NLC + first_result

            case "zeros":
                result = SPACE.join(
                    [__("Zeros"), __("of"), function]
                ) + NLC + first_result

            case "axes_intersection":
                result = SPACE.join(
                    [__("For"), __("function"), function]
                ) + NLC + SPACE.join(
                    [__("Intersection"), __("with"), symbols[0], __("axis")]
                ) + NLC + SPACE.join(
                    [symbols[0], "=", first_result]
                ) + NL + SPACE.join(
                    [__("Intersection"), __("with"), symbols[1], __("axis")]
                ) + NLC + SPACE.join(
                    [symbols[1], "=", second_result]
                )
            case "periodicity":
                result = SPACE.join(
                    [__("Periodicity"), __("of"), function]
                ) + NLC + first_result

            case "convexity":
                result = SPACE.join(
                    [__("Is"), function, __("convex"), "?"]
                ) + NL + first_result

            case "concavity":
                result = SPACE.join(
                    [__("Is"), function, __("concave"), "?"]
                ) + NL + first_result

            case "vertical asymptotes":
                result = SPACE.join(
                    [__("Vertical"), __("asymptotes"), __("of"), function]
                ) + NLC + first_result

            case "horizontal asymptotes":
                result = SPACE.join(
                    [__("Horizontal"), __("asymptotes"), __("of"), function]
                ) + NLC + first_result

            case "slant asymptotes":
                result = SPACE.join(
                    [__("Slant"), __("asymptotes"), __("of"), function]
                ) + NLC + first_result

            case "asymptotes":
                result = SPACE.join(
                    [__("Vertical"), __("asymptotes"), __("of"), function]
                ) + NLC + first_result + NL + SPACE.join(
                    [__("Horizontal"), __("asymptotes"), __("of"), function]
                ) + NLC + second_result + NL + SPACE.join(
                    [__("Slant"), __("asymptotes"), __("of"), function]
                ) + NLC + third_result

            case "evenness":
                result = SPACE.join(
                    [__("Is"), function, __("even"), "?"]
                ) + NL + first_result

            case "oddness":
                result = SPACE.join(
                    [__("Is"), function, __("odd"), "?"]
                ) + NL + first_result

            case "maximum":
                result = SPACE.join(
                    [__("Max"), __("value"), __("of"), function]
                ) + NLC + first_result

            case "minimum":
                result = SPACE.join(
                    [__("Min"), __("value"), __("of"), function]
                ) + NLC + first_result

            case "monotonicity":
                result = SPACE.join(
                    [__("Monotonicity"), __("of"), function]
                ) + NLC + first_result

            case "stationary points":
                result = SPACE.join(
                    [__("Stationary"), __("points"), __("of"), function]
                ) + NLC + first_result

            case _:
                raise ParseError(_("Unknown pattern set: {}").format(pattern_set))

        return result

    @run_asynchronously
    def process_query(self, lang: str = "en") -> list:
        """
        Tries to calculate the requested function
        :param lang:
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
                            raise ParseError(_("Variables can only contain letters\nIncorrect variable: '{}'")
                                             .format(var))

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
                ans = _(m_func.periodicity(symbols[0]), locale=lang)
                result.append(ans)

            case "convexity":
                ans = m_func.convexity(symbols[0])
                result.append(_("Yes", locale=lang) if ans else _("No", locale=lang))

            case "concavity":
                ans = m_func.concavity(symbols[0])
                result.append(_("Yes", locale=lang) if ans else _("No", locale=lang))

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
                ans = m_func.is_even(*symbols)
                result.append(_("Yes", locale=lang) if ans else _("No", locale=lang))

            case "oddness":
                ans = m_func.is_odd(*symbols)
                result.append(_("Yes", locale=lang) if ans else _("No", locale=lang))

            case "maximum":
                result.append(m_func.maximum(symbols[0]))

            case "minimum":
                result.append(m_func.minimum(symbols[0]))

            case "monotonicity":
                result.append(m_func.monotonicity(symbols[0], lang))

            case "stationary points":
                result.append(m_func.stationary_points(symbols[0]))

        return result

    @run_asynchronously
    def parse(self, query: str, lang: str = "en") -> bool:
        """
        Fills in class attributes based on the user request
        Correlates user input with patterns defined in analyse_patterns.json
        Extract function and additional parameters from input query
        :param lang:
        :param query: user input, string (e.g. diff of x**2 by x)
        :return: true on successfully found pattern, false otherwise
        """
        pattern_dict = Config.analysis_patterns

        # Check if input match any pattern
        try:
            pattern_found = self._find_pattern(query, pattern_dict, False, lang)
            if pattern_found is None:
                raise TimeoutError(_("Function execution time limit exceeded! "
                                     "Sorry, it is a very hard problem to solve.",
                                     locale=lang))
            if pattern_found:
                return True
        except ParseError as err:
            # Maybe we should correct some words here. If nothing was changed, then we throw previous exception
            if self._find_pattern(query, pattern_dict, True, lang):
                return True
            raise err

        # If none of patterns were satisfied, then we can try to correct input and match the patterns again
        return self._find_pattern(query, pattern_dict, True, lang)
