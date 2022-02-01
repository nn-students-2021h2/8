import pytest
import source.math.parser as parser
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
def test_parse(expression, result):
    with pytest.raises(result):
        x = parser.Parser.parse(parser.Parser(), expression)
