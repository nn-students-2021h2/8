"""Module with functions for help"""
from random import shuffle
from pathlib import Path

from source.extras.translation import _
import json

examples = json.load(open(Path(__file__).resolve().parent.parent.parent / "resources/examples.json"))


def main_help() -> str:
    """Return main help page"""
    return _('Enter:\n/start to restart bot.\n/graph to draw a graph.\n/analyse to go on to investigate the function.')


def graph_examples() -> list:
    """Return 10 examples for graphs"""
    shuffle(examples['graph'])
    print(examples)
    res = examples['graph'][0:5]
    print(res)
    return res


def graph_guide() -> str:
    """Return graph guide"""
    return _("Graph guide")


def analysis_examples() -> list:
    """Return 10 examples for analysis"""
    shuffle(examples['analysis'])
    res = examples['analysis'][0:5]
    return res


def analysis_guide() -> str:
    """Return analysis guide"""
    return _("Analysis guide")
