import pytest
import source.math.parser as parser


@pytest.mark.parametrize("token, result", [(' x= 1', True),
                                           ('y =x', False),
                                           ('a= 1', True),
                                           ('x ^2=2', True),
                                           ('b^2= a-2', False),
                                           ('qweresdaa', False)])
def test_is_x_equal_num_expression(token, result):
    assert parser.Parser.is_x_equal_num_expression(token) == result
