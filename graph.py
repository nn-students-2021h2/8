"""
Graph class module
"""

import numpy as np
import sympy as sy
from matplotlib import pyplot as plt, style

from parser import Parser


class DrawException(Exception):
    """This exception is raised when sympy cannot draw a function plot"""


# This variable adjusts the accuracy of the implicit function drawing
# Increase it to get more antialiasing result
IMPLICIT_FUNCTION_POINTS = 1000


class Graph:
    """
    This class represents plot of one or multiple functions
    :param file_path: a file name / path which is used to keep plot
    """

    def __init__(self, file_path: str):
        self.plot = sy.plot(show=False)
        self.file_path = file_path

    def setup_plot_style(self):
        """
        Change plot appearance
        # TODO something like json config file in order to set preferred styles
        """

        self.plot.title = "Plot"
        self.plot.legend = True

        style.use('seaborn-whitegrid')

        plt.rcParams['legend.loc'] = "upper right"
        plt.rcParams['legend.frameon'] = True
        plt.rcParams['legend.framealpha'] = 0.6
        plt.rcParams['axes.edgecolor'] = '#1b5756'  # dark green color
        plt.rcParams['xaxis.labellocation'] = 'right'
        plt.rcParams['yaxis.labellocation'] = 'top'
        plt.rcParams['axes.titleweight'] = 'bold'
        plt.rcParams['axes.titlepad'] = 20
        plt.rcParams['axes.labelweight'] = 'bold'
        plt.rcParams['axes.labelpad'] = 0
        plt.rcParams['figure.constrained_layout.use'] = True

    def draw(self, tokens: dict):
        """
        Draw parsed function and save plot as image

        Parameters
        ==========
        :param tokens: dict of parsed user input (see parse function in parser.py to get more info)
            Keys:
            - 'range' : list of two elements - range of the functions (left and right borders)
            - 'explicit' : explicit functions like y = x
            - 'implicit' : implicit functions (it does not have to be truth function),
               for instance, x^2 + y^2 = 4;
               if it is possible, implicit functions are converted into explicit functions
               (for example, y + x = 0 -> y = -x)
            - 'unknown' : expressions that we do not know how to process TODO process this
        """

        x = sy.symbols('x')
        left, right = -10, 10
        expl_func_count = 0

        # Extract function range
        if len(rng := tokens['range']):
            left, right = rng[0], rng[1]

        # Extract all explicit functions
        for expl_func in tokens['explicit']:
            self.plot.extend(sy.plot(expl_func.simplified_expr,
                                     (x, left, right),
                                     show=False))

            self.plot[expl_func_count].label = f'${sy.latex(expl_func.simplified_expr)}$'
            expl_func_count += 1

        # Extract all implicit functions
        for impl_func in tokens['implicit']:
            self.plot.extend(sy.plot_implicit(impl_func.simplified_expr,
                                              (x, left, right),
                                              adaptive=False,
                                              points=IMPLICIT_FUNCTION_POINTS,
                                              show=False,
                                              line_color=list(np.random.rand(3))))

            # Set label 'x = number' if it is expression like 'x = 1'
            label = impl_func.simplified_expr
            is_x_equal_num = Parser.is_x_equal_num_expression(impl_func.expression)
            if is_x_equal_num:
                parts = impl_func.expression.split('=')
                label = sy.Eq(sy.simplify(parts[0]), sy.simplify(parts[1]))

            self.plot.extend(sy.plot(0,
                                     (x, left, right),
                                     label=f'${sy.latex(label)}$',
                                     line_color='none',
                                     show=False))

        # Config plot style and save it
        self.setup_plot_style()

        # Matplotlib does not see plots which were added by 'extend' method.
        # Process_series force mpl process new graphs
        backend = self.plot.backend(self.plot)
        try:
            backend.process_series()
        except (ZeroDivisionError, OverflowError, TypeError) as err:
            raise DrawException("Unexpected error, check your expression.") from err

        # Set colors on implicit functions in legend. I had to do it because Sympy don't want to
        # add these functions in legend by itself.
        # Print self.plot variable to understand why it is needed
        legend = backend.ax[0].get_legend()
        impl_func_count = len(tokens['implicit'])
        expl_func_count = len(tokens['explicit'])
        counter = 0
        for i in range(expl_func_count, expl_func_count + 2 * impl_func_count, 2):
            legend.legendHandles[expl_func_count + counter].set_color(self.plot[i].line_color)
            counter += 1

        backend.fig.savefig(self.file_path, dpi=300, bbox_inches='tight')
        plt.close()
