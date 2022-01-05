"""
Math Function class module
"""


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

    def __init__(self, expression, simplified_expr, func_type, symbols=None):
        if symbols is None:
            symbols = []
        self.expression = expression
        self.simplified_expr = simplified_expr
        self.func_type = func_type
        self.symbols = symbols

    def __str__(self):
        return self.expression
