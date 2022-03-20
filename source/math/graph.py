"""
Graph class module
"""
import multiprocessing
from io import BytesIO

import numpy as np
import sympy as sy
from matplotlib import pyplot as plt, style

from source.conf.config import Config
from source.extras.translation import _
from source.math.graph_parser import GraphParser


class DrawError(Exception):
    """This exception is raised when sympy cannot draw a function plot"""


class Graph:
    """This class represents plot of one or multiple functions"""

    # This variable adjusts the accuracy of the implicit function drawing
    # Increase it to get more antialiasing result
    IMPLICIT_FUNCTION_POINTS = Config().properties["PLOT_APPEARANCE"]["STYLE"]["implicit_function_points"]

    def __init__(self):
        self.plot = sy.plot(show=False, title=_("Plot"), legend=True)

    @staticmethod
    def setup_plot_style():
        """
        Change plot appearance
        """
        parameters = Config().properties["PLOT_APPEARANCE"]
        style.use(parameters["STYLE"]["style"])

        for param, value in parameters["RC_PARAMS"].items():
            plt.rcParams[param] = value

    def draw(self, parser: GraphParser, lang: str = "en", q: multiprocessing.Queue = None) -> BytesIO:
        """
        Draw parsed functions and save plot as image

        Parameters
        ==========
        :param q:
        :param lang:
        :param parser: parser that contain tokens;
        tokens: dict of parsed user input (see parse function in graph_parser.py to get more info)
            Keys:
            - 'aspect ratio' : the ratio of x to y
            - 'domain' : list of left and right x-limit
            - 'range' : list of two elements - range of the functions (left and right borders)
            - 'explicit' : explicit functions like y = x
            - 'implicit' : implicit functions (it does not have to be truth function),
               for instance, x^2 + y^2 = 4;
        """
        legend_len_limit = 60
        func_len_limit = 300
        tokens = parser.tokens

        # We have to set domain and/or range due to functions are calculating in given intervals and if we don't
        # explicitly specify it, then later functions will be displayed cropped

        # Get function range for plotting functions
        if len(rng := tokens["range"]) != 2:
            rng = [-10, 10]

        # Get function domain for plotting functions
        if len(domain := tokens["domain"]) != 2:
            domain = [-10, 10]

        x, y = sy.symbols("x y")

        # Variable that mark the graph having long functions
        long_func = False

        # Extract all explicit functions
        for func in tokens['explicit']:
            label = f'${sy.latex(func.simplified_expr)}$'
            if len(func) >= func_len_limit:
                parser.push_warning(_("NOTE: some of the functions are extremely long! Graph may be incorrect.",
                                      locale=lang))
            if len(func) > legend_len_limit:
                label = str(func.simplified_expr)[:legend_len_limit] + "..."
                long_func = True

            self.plot.extend(sy.plot(func.simplified_expr,
                                     (x, domain[0], domain[1]),
                                     show=False,
                                     label=label))

        # Update plot parameters and y-limit for implicit functions
        backend = self.plot.backend(self.plot)
        try:
            backend.process_series()
        except (ZeroDivisionError, OverflowError, TypeError):
            q.put(DrawError(_("Unexpected error, check your expression.", locale=lang)))

        # Extract all implicit functions
        for func in tokens['implicit']:
            if len(func) >= func_len_limit:
                parser.push_warning(_("NOTE: some of the functions are extremely long! Graph may be incorrect.",
                                      locale=lang))
            self.plot.extend(sy.plot_implicit(func.simplified_expr,
                                              (x, domain[0], domain[1]),
                                              (y, rng[0], rng[1]),
                                              adaptive=False,
                                              points=self.IMPLICIT_FUNCTION_POINTS,
                                              show=False,
                                              line_color=list(np.random.rand(3))))

            # Set label 'x = number' if it is expression like 'x = 1'
            label = func.simplified_expr
            if GraphParser.is_x_equal_num_expression(func.expression):
                label = sy.Eq(func.symbols[0], sy.solve(func.simplified_expr)[0])

            label = f'${sy.latex(func.simplified_expr)}$'
            if len(func) > legend_len_limit:
                label = str(func.simplified_expr)[:legend_len_limit] + "..."
                long_func = True
            self.plot.extend(sy.plot(0,
                                     label=label,
                                     line_color='none',
                                     show=False))

        # Matplotlib does not see plots which were added by 'extend' method.
        # Process_series force mpl process new graphs
        backend = self.plot.backend(self.plot)
        try:
            backend.process_series()
        except (ZeroDivisionError, OverflowError, TypeError):
            q.put(DrawError(_("Unexpected error, check your expression.", locale=lang)))

        # Check if some functions were shrunk
        if long_func:
            parser.push_warning(_("Some functions have been reduced because they are too long.", locale=lang))

        # Set function range
        if len(rng := tokens["range"]) != 0:
            plt.ylim(rng)

        # Set function domain
        if len(domain := tokens["domain"]) != 0:
            plt.xlim(domain)

        # Set aspect ratio
        if len(ratio := tokens["aspect ratio"]) != 0:
            backend.ax[0].set_aspect(ratio[0])

        # Set colors on implicit functions in legend. I had to do it because Sympy don't want to
        # add these functions in legend by itself.
        # Print self.plot variable to understand why it is needed
        legend = backend.ax[0].get_legend()
        impl_func_count = len(tokens["implicit"])
        expl_func_count = len(tokens["explicit"])
        counter = 0
        for i in range(expl_func_count, expl_func_count + 2 * impl_func_count, 2):
            legend.legendHandles[expl_func_count + counter].set_color(self.plot[i].line_color)
            counter += 1

        buf = BytesIO()
        backend.fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close("all")

        q.put(buf)
