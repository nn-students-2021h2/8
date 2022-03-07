"""
Math Function class module
"""

import sympy as sy
import sympy.calculus.util as calculus


def replace_incorrect_functions(function: str) -> str:
    """
    Some functions in Sympy are named differently from what we are used to
    Our interpretation -> Sympy view:
    tg -> tan
    ctg -> cot
    arcsin -> asin
    arccos -> acos
    arctg -> atan
    arcctg -> acot
    :param function: a string representation of a function
    :return: function with replacements applied
    """
    replacements = {
        "tg": "tan",
        "ctg": "cot",
        "arcsin": "asin",
        "arccos": "acos",
        "arctg": "atan",
        "arctan": "atan",
        "arcctg": "acot",
        "arccot": "acot"
    }
    result = function
    for key, value in replacements.items():
        result = result.replace(key, value)

    return result


class MathFunction:
    """
    This class represents a plot of function

    Parameters
    ==========
    :param expression: input string from user
    :param simplified_expr: sympy parsed math expression. It is used in sympy calculations
    :param func_type: "explicit" or "implicit" function type. It is used in plotting in mainly
    :param symbols: a list of math expression variables
    """

    def __init__(self, expression: str, simplified_expr, func_type="explicit", symbols=None):
        if symbols is None:
            symbols = []
        self.expression = expression
        self.simplified_expr = simplified_expr
        self.func_type = func_type
        self.symbols = symbols

    def __str__(self):
        return self.expression

    def derivative(self, *symbols: sy.S) -> sy.Function:
        """
        Calculates the derivative by given variables
        :param symbols: the variables to be differentiated by
        :return: a derivative of the function (it is also function)
        """
        diff_function = self.simplified_expr

        try:
            if len(symbols) == 0:
                diff_function = sy.diff(self.simplified_expr)
            else:
                for symbol in symbols:
                    diff_function = sy.diff(diff_function, symbol)
        except ValueError as err:
            raise ValueError(f"Since there is more than one variable in the expression, "
                             f"the variable(s) of differentiation must be supplied to "
                             f"differentiate:\n{self.expression}") from err

        return diff_function

    def domain(self, symbol: sy.S) -> sy.Interval:
        """
        Finds the definition area
        :param symbol: the symbol to find the definition (it is 'x' by default)
        :return: an interval the interval over which the function is defined
        """
        return calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)

    def frange(self, symbol: sy.Symbol) -> sy.Interval:
        """
        Finds value range of the function
        :param symbol: the symbol to find the area (it is 'y' by default)
        :return: a value range (interval) of the function
        """
        return calculus.function_range(self.simplified_expr, symbol, sy.S.Reals)

    def zeros(self) -> sy.Set:
        """
        Calculates where the function turns to zero
        :return: a set of the 'x' values
        """
        function = self.simplified_expr

        # if it is expression like 'y + x', then replace 'y' with zero
        if len(self.symbols) > 1:
            function = function.subs(self.symbols[1], 0)
        return sy.solveset(sy.Eq(function, 0), self.symbols[0])

    def axis_intersection(self, target_symbol: sy.Symbol, zero_symbol: sy.Symbol) -> sy.Set:
        """
        Calculates the value of the variable 'target_symbol' at which the function crosses the axis 'target_symbol'
        For example, y = x + 1 -> the function intersect x-axis at x = -1 and intersect y-axis at y = 1
        :param target_symbol: the axis about which the intersection is defined
        :param zero_symbol: another axis that should be zeroed
        :return: a set of answers
        """
        solutions = set()
        partly_solved = self.simplified_expr.subs(zero_symbol, 0)
        if target_symbol not in partly_solved.free_symbols:
            solutions.add(partly_solved)
        else:
            solutions = sy.solveset(partly_solved, target_symbol)
        return solutions

    def periodicity(self, symbol: sy.Symbol):
        """
        Finds interval of periodicity
        :param symbol: see 'periodicity' arguments
        :return: see return of the 'periodicity' function
        """
        return calculus.periodicity(self.simplified_expr, symbol)

    def convexity(self, symbol: sy.Symbol) -> bool:
        """
        Determine if the function is convex
        :return: true if it is convex, false otherwise
        """
        return calculus.is_convex(self.simplified_expr, symbol)

    def concavity(self, symbol: sy.Symbol) -> bool:
        """
        Determine if the function is concave
        :return: true if it is concave, false otherwise
        """
        return calculus.is_convex(-self.simplified_expr, symbol)

    def continuity(self, symbol: sy.Symbol) -> sy.Interval:
        """
        Finds interval of continuity
        :param symbol: see 'continuous_domain' arguments
        :return: an interval of continuity
        """
        return calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)

    def is_even(self, *symbols) -> bool:
        """
        Determine if the function is even
        :param symbols: all function variables (just 'x').
        :return: true if the function is even, false otherwise
        """
        function = sy.simplify(self.simplified_expr)
        if len(function.free_symbols) == 0:
            return True

        x = symbols[0]
        even_func = function.subs(x, -x)

        return even_func == function

    def is_odd(self, *symbols) -> bool:
        """
        Determine if the function is odd
        :param symbols: all function variables
        :return: true if the function is odd, false otherwise
        """
        function = sy.simplify(self.simplified_expr)

        x = symbols[0]
        y = symbols[1] if len(symbols) > 1 else None

        even_func = function.subs(x, -x)

        if y is not None:
            odd_func = function.subs(y, (-1) * y)
            return even_func in (odd_func, -odd_func)

        return even_func == sy.simplify(function * (-1))

    def vertical_asymptotes(self, symbol: sy.Symbol) -> set:
        """
        Try to find vertical asymptotes of the function
        :param symbol: the variable in relation to which the limits will be considered (x by default)
        :return: a set of answers (functions)
        """
        exist = calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)
        not_exist = sy.S.Reals - exist

        if isinstance(not_exist, sy.sets.sets.Union):
            not_exist = not_exist.args
        else:
            not_exist = [not_exist]

        ans = set()
        for values in not_exist:
            if isinstance(values, sy.sets.sets.FiniteSet):
                for cur in values:
                    left_limit = sy.limit(self.simplified_expr, symbol, cur, '+')
                    right_limit = sy.limit(self.simplified_expr, symbol, cur, '-')
                    if left_limit.is_infinite or right_limit.is_infinite:
                        ans.add(cur)
            elif isinstance(values, sy.sets.sets.Interval):
                for cur in values.args[0:2]:
                    left_limit = sy.limit(self.simplified_expr, symbol, cur, '+')
                    right_limit = sy.limit(self.simplified_expr, symbol, cur, '-')
                    if left_limit.is_infinite or right_limit.is_infinite:
                        ans.add(cur)

        if len(ans) == 0:
            ans.add(sy.EmptySet)

        return ans

    def horizontal_asymptotes(self, symbol: sy.Symbol) -> set:
        """
        Try to find horizontal asymptotes of the function
        :param symbol: the variable in relation to which the limits will be considered (x by default)
        :return: a set of answers (functions)
        """
        pos_limit = sy.limit(self.simplified_expr, symbol, sy.oo)
        neg_limit = sy.limit(self.simplified_expr, symbol, -sy.oo)
        ans = set()

        if pos_limit.is_number and pos_limit.is_finite:
            ans.add(pos_limit)
        if neg_limit.is_number and neg_limit.is_finite:
            ans.add(neg_limit)

        if len(ans) == 0:
            ans.add(sy.EmptySet)

        return ans

    def slant_asymptotes(self, symbol: sy.Symbol) -> set:
        """
        Try to find slant (in particular, horizontal) asymptotes of the function
        :param symbol: the variable in relation to which the limits will be considered (x by default)
        :return: a set of answers (functions)
        """
        ans = set()

        # TODO periodic function

        k = sy.limit(self.simplified_expr / symbol, symbol, sy.oo)
        if k.is_number and k.is_finite:
            b = sy.limit(self.simplified_expr - k * symbol, symbol, sy.oo)
            if b.is_number:
                ans.add(k * symbol + b)

        k = sy.limit(self.simplified_expr / symbol, symbol, -sy.oo)
        if k.is_number and k.is_finite:
            b = sy.limit(self.simplified_expr - k * symbol, symbol, -sy.oo)
            if b.is_number:
                ans.add(k * symbol + b)

        # If given function is line, then it is its own asymptote, so we should remove it from set
        ans.discard(self.simplified_expr)

        if len(ans) == 0:
            ans.add(sy.EmptySet)

        return ans

    def maximum(self, symbol: sy.Symbol) -> sy.Number:
        """
        Tries to find maximum value (not local maximums!) of the function
        :param symbol: see 'maximum' function args
        :return: a maximum value or empty set
        """
        maximum = calculus.maximum(self.simplified_expr, symbol)
        if not maximum.is_infinite and not maximum.is_number:
            return sy.EmptySet
        return maximum

    def minimum(self, symbol: sy.Symbol) -> sy.Number:
        """
        Tries to find minimum value (not local minimums!) of the function
        :param symbol: see 'minimum' function args
        :return: a minimum value or empty set
        """
        minimum = calculus.minimum(self.simplified_expr, symbol)
        if not minimum.is_infinite and not minimum.is_number:
            return sy.EmptySet
        return minimum

    def stationary_points(self, symbol: sy.Symbol) -> sy.Set:
        """
        Tries to find points of the function where derivative is zero
        :param symbol: see 'stationary_points' function args
        :return: a set of answers
        """
        return calculus.stationary_points(self.simplified_expr, symbol)
