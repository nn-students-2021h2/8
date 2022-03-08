"""
Tests for calculus parser
"""

import pytest

import source.math.calculus_parser as parser
from source.math.parser import ParseError


@pytest.mark.parametrize('expr, result', [('dif x+2', True),
                                          ('diff y = x', True),
                                          ('[kw w', False),
                                          ('doman sin(x)+2', True),
                                          ('rang x**2+4', True),
                                          ('stationary points x+3-ln(x)', True),
                                          ('periodycity x**5-5=y', True),
                                          ('continuity x+4-8', True),
                                          ('convexity 10-x+2*x', True),
                                          ('concavty sin(x)+2', True),
                                          ('horizontal asymptotes 3*1/x', True),
                                          ('vertical asymptotes of tan(x)', True),
                                          ('asymptotes ctan(x)', True),
                                          ('evenes of cos(x)', True),
                                          ('odnes cos(x+2)', True),
                                          ('axes intersection of y=x**2+2*x-20', True),
                                          ('slanc asiptotes 1/x*2', True),
                                          ('maximum -x**2', True),
                                          ('minm x^2', True),
                                          ('zeroz -x**2+12*x+100', True)])
@pytest.mark.asyncio
async def test_parse_success(expr, result):
    assert await parser.CalculusParser.parse(parser.CalculusParser(), expr) == result


@pytest.mark.parametrize("expr, exception", [('diff [', ParseError),
                                             ('diff [1]', AttributeError),
                                             ('diff y=', ParseError)])
@pytest.mark.asyncio
async def test_parse_error(expr, exception):
    with pytest.raises(exception):
        await parser.CalculusParser.parse(parser.CalculusParser(), expr)
