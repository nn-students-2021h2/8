"""Module with functions for help"""
import json
from pathlib import Path
from random import shuffle

from source.extras.translation import _
from jsonschema import validate, ValidationError

examples_schema = {
    "type": "object",
    "properties": {
        "graph": {
            "type": "array",
            "uniqueItems": True,
            "contains": {
                "type": "string"
              }
        },
        "analysis": {
            "type": "array",
            "uniqueItems": True,
            "contains": {
                "type": "string"
              }
        }
    }
}

with open(Path(__file__).resolve().parents[2] / "resources/examples.json", encoding="utf-8") as f:
    examples = json.load(f)
    try:
        validate(examples, examples_schema)
    except ValidationError as err:
        raise Exception("File examples.json does not match examples_schema") from err


def main_help() -> str:
    """Return main help page"""
    return _('Enter:\n/start to restart bot.\n/graph to draw a graph.\n/analyse to go on to investigate the function.')


def graph_examples() -> list:
    """Return 5 examples for graphs"""
    shuffle(examples['graph'])
    res = examples['graph'][0:5]
    return res


def analysis_examples() -> list:
    """Return 5 examples for analysis"""
    shuffle(examples['analysis'])
    res = examples['analysis'][0:5]
    return res
