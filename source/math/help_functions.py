"""Module with functions for help"""
from source.extras.translation import _


def main_help() -> str:
    """Return main help page"""
    return _('Enter:\n/start to restart bot.\n/graph to draw a graph.\n/analyse to go on to investigate the function.')


def graph_examples() -> list:
    """Return 10 examples for graphs"""
    res = ["/graph x+2", "/graph sin x", "/graph x**2", "/graph log x", "/graph x^3+2*x^2-12x",
           "/graph y=1/x", "/graph tg(sin(x))", "/graph 21*2**x", "/graph 12-x*2", "/graph y=3"]
    return res


def graph_guide() -> str:
    """Return graph guide"""
    return _("Graph guide")


def analysis_examples() -> list:
    """Return 10 examples for analysis"""
    res = ["/analyse diff x^4+12x^2-7x", "/analyse range sin(3x)", "/analyse period tan(3x)",
           "/analyse diff x^4+12x^2-7x", "/analyse range sin(3x)", "/analyse diff x^4+12x^2-7x",
           "/analyse range sin(3x)", "/analyse period tan(3x)", "/analyse zeros x**2-10", "/analyse max sin(x)"]
    return res


def analysis_guide() -> str:
    """Return analysis guide"""
    return _("Analysis guide")
