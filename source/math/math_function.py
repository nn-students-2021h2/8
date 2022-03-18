"""
Math Function class module
"""

import sympy as sy
import sympy.calculus.util as calculus
from sympy.utilities.iterables import iterable

from source.extras.translation import _


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
        "arcsin": "asin",
        "arccos": "acos",
        "arctg": "atan",
        "arctan": "atan",
        "arcctg": "acot",
        "arccot": "acot",
        "ctg": "cot",
        "tg": "tan"
    }
    result = function
    for key, value in replacements.items():
        result = result.replace(key, value)

    return result


class MathError(Exception):
    """Special exception for custom mathematical errors handling"""


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

    def __init__(self, expression: str, simplified_expr: (sy.Expr | sy.Eq), func_type: str = "explicit",
                 symbols: list = None):
        if symbols is None:
            symbols = []
        self.expression = expression
        self.simplified_expr = simplified_expr
        self.func_type = func_type
        self.symbols = symbols

    def __str__(self):
        return self.expression

    @staticmethod
    def _checkStationaryPoints(function: sy.Expr, symbol: sy.Symbol, domain: sy.Interval) -> bool:
        """
        Fix bug fix infinite loop when Sympy calculates stationary points of aperiodic function.
        Return false if function has more than CRIT_POINTS_LIMIT stationary points, true otherwise
        """
        period = sy.periodicity(function, symbol)
        if period == sy.S.Zero:
            # the expression is constant wrt symbol
            return True

        if period is not None:
            if isinstance(domain, sy.Interval):
                if (domain.inf - domain.sup).is_infinite:
                    domain = sy.Interval(0, period)
            elif isinstance(domain, sy.Union):
                for sub_dom in domain.args:
                    if isinstance(sub_dom, sy.Interval) and (sub_dom.inf - sub_dom.sup).is_infinite:
                        domain = sy.Interval(0, period)

        intervals = calculus.continuous_domain(function, symbol, domain)
        if isinstance(intervals, (sy.Interval, sy.FiniteSet)):
            interval_iter = (intervals,)
        elif isinstance(intervals, sy.Union):
            interval_iter = intervals.args
        else:
            return False

        for interval in interval_iter:
            if isinstance(interval, sy.Interval):
                critical_points = sy.S.EmptySet
                solution = sy.solveset(function.diff(symbol), symbol, interval)

                if not iterable(solution):
                    return False
                if isinstance(solution, sy.ImageSet):
                    return False

                critical_points += solution

                count = 0
                for _ in critical_points:
                    count += 1
                    if count > 100:
                        return False
        return True

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
            raise MathError(_("Since there is more than one variable in the expression, "
                              "the variable(s) of differentiation must be supplied to "
                              "differentiate")) from err

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
        if not self._checkStationaryPoints(self.simplified_expr, symbol, sy.S.Reals):
            raise ValueError
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
        return sy.solveset(sy.Eq(function, 0), self.symbols[0], sy.S.Reals)

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

    def periodicity(self, symbol: sy.Symbol) -> (0, None, sy.Function):
        """
        Finds interval of periodicity
        :param symbol: see 'periodicity' arguments
        :return: see return of the 'periodicity' function
        """
        result = calculus.periodicity(self.simplified_expr, symbol)
        if result is None:
            result = _("Aperiodic function")
        if result == 0:
            result = _("Function is constant (any period)")
        return result

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
        # TODO unused function. For now
        return calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)

    def monotonicity(self, symbol: sy.Symbol, lang: str = "en") -> str:
        """
        Determines the type of monotonicity of the function
        :param lang:
        :param symbol: the argument of the function ('x')
        :return: type of function as string
        """
        types = {
            sy.is_strictly_decreasing: _("Strictly decreasing", locale=lang),
            sy.is_strictly_increasing: _("Strictly increasing", locale=lang),
            sy.is_increasing: _("Increasing", locale=lang),
            sy.is_decreasing: _("Decreasing", locale=lang)
        }
        for func, value in types.items():
            if func(self.simplified_expr, symbol=symbol):
                return value
        return _("Non-monotonic", locale=lang)

    def is_even(self, *symbols: sy.Symbol) -> bool:
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

        return sy.simplify(even_func) == function

    def is_odd(self, *symbols: sy.Symbol) -> bool:
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

        return sy.simplify(even_func) == sy.simplify(-function)

    def _check_v_asymptote(self, symbol, point) -> bool:
        left_limit = sy.limit(self.simplified_expr, symbol, point, '+')
        right_limit = sy.limit(self.simplified_expr, symbol, point, '-')
        return not point.is_infinite and (left_limit.is_infinite or right_limit.is_infinite)

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
        for value in not_exist:
            if isinstance(value, sy.sets.sets.FiniteSet):
                for cur in value:
                    if self._check_v_asymptote(symbol, cur):
                        ans.add(cur)
            elif isinstance(value, sy.sets.sets.Interval):
                for cur in value.args[0:2]:
                    if self._check_v_asymptote(symbol, cur):
                        ans.add(cur)

        # If function is periodic, we can't yet give an accurate answer
        if calculus.periodicity(self.simplified_expr, symbol):
            # If the domain of function is some kind of "R \ {...}", than we can omit the part "R \"
            if isinstance(exist, sy.Complement):
                ans.add(exist.args[1])
            else:
                ans.add(not_exist[0])

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
            if b.is_number and b.is_finite:
                ans.add(k * symbol + b)

        k = sy.limit(self.simplified_expr / symbol, symbol, -sy.oo)
        if k.is_number and k.is_finite:
            b = sy.limit(self.simplified_expr - k * symbol, symbol, -sy.oo)
            if b.is_number and b.is_finite:
                ans.add(k * symbol + b)

        # If given function is line, then it is its own asymptote, so we should remove it from set
        ans.discard(self.simplified_expr)

        if len(ans) == 0:
            ans.add(sy.EmptySet)

        return ans

    def maximum(self, symbol: sy.Symbol) -> (sy.Number, sy.EmptySet):
        """
        Tries to find maximum value (not local maximums!) of the function
        :param symbol: see 'maximum' function args
        :return: a maximum value or empty set
        """
        if not self._checkStationaryPoints(self.simplified_expr, symbol, sy.S.Reals):
            raise ValueError
        maximum = calculus.maximum(self.simplified_expr, symbol)
        if not maximum.is_infinite and not maximum.is_number:
            return sy.EmptySet
        return maximum

    def minimum(self, symbol: sy.Symbol) -> (sy.Number, sy.EmptySet):
        """
        Tries to find minimum value (not local minimums!) of the function
        :param symbol: see 'minimum' function args
        :return: a minimum value or empty set
        """
        if not self._checkStationaryPoints(self.simplified_expr, symbol, sy.S.Reals):
            raise ValueError
        minimum = calculus.minimum(self.simplified_expr, symbol)
        if not minimum.is_infinite and not minimum.is_number:
            return sy.EmptySet
        return minimum

    def stationary_points(self, symbol: sy.Symbol) -> (sy.Set, sy.EmptySet):
        """
        Tries to find points of the function where derivative is zero
        :param symbol: see 'stationary_points' function args
        :return: a set of answers
        """
        return calculus.stationary_points(self.simplified_expr, symbol)
