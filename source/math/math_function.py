"""
Math Function class module
"""

import sympy as sy
import sympy.calculus.util as calculus


class MathFunction:
    """
    This class represents a plot of function

    Parameters
    ==========
    :param expression: input string from user
    :param simplified_expr: sympy parsed math expression. It is used in sympy calculations
    :param func_type: "explicit" or "implicit" function type. It is used in plotting in mainly
    :param symbols: list of math expression variables
    """

    def __init__(self, expression: str, simplified_expr: sy.Function, func_type="explicit", symbols=None):
        if symbols is None:
            symbols = []
        self.expression = expression
        self.simplified_expr = simplified_expr
        self.func_type = func_type
        self.symbols = symbols

    def __str__(self):
        return self.expression

    def derivative(self, *symbols: sy.S) -> sy.Function:
        diff_function = self.simplified_expr

        try:
            if len(symbols) == 0:
                diff_function = sy.diff(self.simplified_expr)
            else:
                for symbol in symbols:
                    diff_function = sy.diff(diff_function, symbol)
        except ValueError as err:
            raise ValueError(f"Since there is more than one variable in the expression, "
                             f"the variable(s) of differentiation must be supplied to differentiate\n{self.expression}")

        return diff_function

    def domain(self, symbol: sy.S) -> sy.Interval:
        return calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)

    def frange(self, symbol: sy.Symbol) -> sy.Interval:
        return calculus.function_range(self.simplified_expr, symbol, sy.S.Reals)

    # TODO solveset ?
    def zeros(self) -> sy.Set:
        return sy.solveset(sy.Eq(self.simplified_expr, 0))

    def axis_intersection(self, target_symbol: sy.Symbol, zero_symbol: sy.Symbol) -> sy.Set:
        partly_solved = self.simplified_expr.subs(zero_symbol, 0)
        return sy.solveset(partly_solved, target_symbol)

    def periodicity(self, symbol: sy.Symbol):
        return calculus.periodicity(self.simplified_expr, symbol)

    def convexity(self) -> bool:
        return calculus.is_convex(self.simplified_expr)

    def concavity(self) -> bool:
        return not calculus.is_convex(self.simplified_expr)

    def continuity(self, symbol: sy.Symbol) -> sy.Interval:
        return calculus.continuous_domain(self.simplified_expr, symbol, sy.S.Reals)

    def is_even(self, *symbols):
        function = sy.simplify(self.simplified_expr)
        test = function.free_symbols
        if len(function.free_symbols) == 0:
            return True

        x = symbols[0]
        even_func = function.subs(x, -x)

        if even_func == function:
            return True
        else:
            return None

    def is_odd(self, *symbols):
        function = sy.simplify(self.simplified_expr)

        x = symbols[0]
        y = symbols[1] if len(symbols) > 1 else None

        even_func = function.subs(x, -x)

        if y is not None:
            odd_func = function.subs(y, -y)
            if even_func == odd_func or even_func == -odd_func:
                return True
            else:
                return None
        else:
            if even_func == sy.simplify(function * (-1)):
                return True
            else:
                return None

    def vertical_asymptotes(self, symbol: sy.Symbol) -> set:
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
            else:
                ans.add(values)

        return ans

    def horizontal_asymptotes(self, symbol: sy.Symbol) -> set:
        pos_limit = sy.limit(self.simplified_expr, symbol, sy.oo)
        neg_limit = sy.limit(self.simplified_expr, symbol, -sy.oo)
        ans = set()

        if pos_limit.is_finite:
            ans.add(pos_limit)
        if neg_limit.is_finite:
            ans.add(neg_limit)

        return ans

    def slant_asymptotes(self, symbol: sy.Symbol) -> set:
        k = None
        b = None
        ans = set()

        # TODO periodic function

        k = sy.limit(self.simplified_expr / symbol, symbol, sy.oo)
        if k.is_finite:
            b = sy.limit(self.simplified_expr - k * symbol, symbol, sy.oo)
            if b.is_finite:
                ans.add(k * symbol + b)

        k = sy.limit(self.simplified_expr / symbol, symbol, -sy.oo)
        if k.is_finite:
            b = sy.limit(self.simplified_expr - k * symbol, symbol, -sy.oo)
            if b.is_finite:
                ans.add(k * symbol + b)

        return ans
