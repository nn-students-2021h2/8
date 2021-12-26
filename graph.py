import numpy as np
import sympy as sy
from matplotlib import pyplot as plt, style


# This exception raise when sympy cannot draw a function plot
class DrawException(Exception):
    pass


# The class represents a plot of function with attributes 'expression' - list of string arguments, that can be converted
# into math expression;
# 'simplified_expr' - sympy math expression
# 'func_type' - "explicit" or "implicit" function type
# 'symbols' - list of math expression variables
class Graph:
    def __init__(self, expression, simplified_expr, func_type, symbols=None):
        if symbols is None:
            symbols = []
        self.expression = expression
        self.simplified_expr = simplified_expr
        self.func_type = func_type
        self.symbols = symbols

    def __str__(self):
        return self.expression

    # Parse tokens and save plot in file 'self.file_path'
    @staticmethod
    def draw(tokens, file_path):
        x, y = sy.symbols('x y')
        p = sy.plot()
        left, right = -10, 10
        func_count = 0

        # Extract function range
        if len(rng := tokens['range']):
            p.xlim, p.ylim = rng, rng
            left, right = rng[0], rng[1]

        # Extract all implicit functions
        for impl_func in tokens['implicit']:
            if len(impl_func.symbols) == 0:
                p.extend(sy.plot(impl_func.simplified_expr,
                                 (x, left, right),
                                 show=False))
            else:
                p.extend(sy.plot(impl_func.simplified_expr,
                                 (impl_func.symbols[0], left, right),
                                 show=False))

            p[func_count].label = '$%s$' % sy.latex(impl_func.simplified_expr)
            func_count += 1

        # Extract all explicit functions
        for expl_func in tokens['explicit']:
            p.extend(sy.plot_implicit(expl_func.simplified_expr,
                                      (expl_func.symbols[0], left, right),
                                      (expl_func.symbols[1], left, right),
                                      adaptive=False,
                                      show=False,
                                      line_color=list(np.random.rand(3))))

        # Config plot style
        p.title = 'Plot'
        p.legend = True
        p.aspect_ratio = (1, 1)

        style.use('seaborn-whitegrid')
        plt.rcParams['legend.loc'] = "upper right"
        plt.rcParams['lines.linewidth'] = 2
        plt.rcParams['xaxis.labellocation'] = 'right'
        plt.rcParams['yaxis.labellocation'] = 'top'
        plt.rcParams['axes.titleweight'] = 'bold'
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.titlepad'] = 20
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.labelweight'] = 'bold'
        plt.rcParams['axes.labelpad'] = -2

        # p.show()
        p.save(file_path)
