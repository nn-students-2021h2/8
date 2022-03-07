"""
Tests for graph parser
"""

import pytest

import source.math.graph_parser as parser
from source.math.parser import ParseError


@pytest.mark.parametrize("token, result", [(' x= 1', True),
                                           ('y =x', False),
                                           ('a= 1', True),
                                           ('x ^2=2', True),
                                           ('b^2= a-2', False),
                                           ('qweresdaa', False)])
def test_is_x_equal_num_expression(token, result):
    assert parser.Parser.is_x_equal_num_expression(token) == result


@pytest.mark.parametrize("expression, result", [("x, y, z, w, e, r, t, y, u, i, o, p, a, s, d, f, g, h", ParseError),
                                                ("3y", ParseError),
                                                ("y = 10sin(x)", ParseError),
                                                ("y=x=z", ParseError),
                                                ("y=4*x, from a to b", ParseError),
                                                ("y=4*x+3*z", ParseError),
                                                ("y=2+x, from 6 to 1", ParseError),
                                                ("x^2, from ", ParseError)])
@pytest.mark.asyncio
async def test_parse(expression, result):
    with pytest.raises(result):
        await parser.GraphParser.parse(parser.GraphParser(), expression)


@pytest.mark.parametrize("expr, result", [('x*4', ['x*4']),
                                          ('sin( 2* x) + 12\n 10\nx*2', ['sin( 2* x) + 12', ' 10', 'x*2']),
                                          ('xxxx', ['xxxx']),
                                          ('1\n2\n2\n*\n', ['1', '2', '2', '*', ''])])
def test_split_query_success(expr, result):
    assert parser._split_query(expr) == result


@pytest.mark.parametrize("expr, result", [('(((', ParseError),
                                          ('))}{{}', ParseError),
                                          (')(x*2', ParseError)])
def test_split_query_error(expr, result):
    with pytest.raises(result):
        parser._split_query(expr)
