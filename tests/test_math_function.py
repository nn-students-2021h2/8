"""
Tests for math functions
"""

import pytest
import sympy

import source.math.math_function as math_f


@pytest.mark.parametrize('incorrect, correct', [('sin(x)+tg(x+2)', 'sin(x)+tan(x+2)'),
                                                ('ctg(x+4)', 'cot(x+4)'),
                                                ('arcsin(x)', 'asin(x)'),
                                                ('arccos(x)', 'acos(x)'),
                                                ('arctg(2*x)+sin(x)-log(10-x)', 'atan(2*x)+sin(x)-log(10-x)'),
                                                ('arcctg(x)', 'acot(x)'),
                                                ('arccot(x)', 'acot(x)')])
def test_replace_incorrect_functions(incorrect, correct):
    assert math_f.replace_incorrect_functions(incorrect) == correct


