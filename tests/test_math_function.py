"""
Tests for math functions
"""

import pytest
from source.math.math_function import MathFunction
from sympy.abc import x, y

import source.math.math_function as math_f
import sympy as sy


@pytest.mark.parametrize('incorrect, correct', [('sin(x)+tg(x+2)', 'sin(x)+tan(x+2)'),
                                                ('ctg(x+4)', 'cot(x+4)'),
                                                ('arcsin(x)', 'asin(x)'),
                                                ('arccos(x)', 'acos(x)'),
                                                ('arctg(2*x)+sin(x)-log(10-x)', 'atan(2*x)+sin(x)-log(10-x)'),
                                                ('arcctg(x)', 'acot(x)'),
                                                ('arccot(x)', 'acot(x)')])
def test_replace_incorrect_functions(incorrect, correct):
    assert math_f.replace_incorrect_functions(incorrect) == correct


@pytest.mark.parametrize("expr, result", [
    (MathFunction("", x ** 5 + 3 * x ** 4 - 2 * x ** 2 + x - 10), 5 * x ** 4 + 12 * x ** 3 - 4 * x + 1),
    (MathFunction("", sy.sin(3 * x ** 2)), 6 * x * sy.cos(3 * x ** 2)),
    (MathFunction("", sy.cos(3 * x + 1)), -3 * sy.sin(3 * x + 1)),
    (MathFunction("", (x ** 2 - 2 * x + 3) ** 5), 10 * (x - 1) * (x ** 2 - 2 * x + 3) ** 4),
    (MathFunction("", sy.sqrt(x)), 1 / (2 * sy.sqrt(x))),
    (MathFunction("", sy.asin(x) ** 2), 2 * sy.asin(x) * (1 / (sy.sqrt(1 - x ** 2)))),
    (MathFunction("", sy.exp(sy.sqrt(sy.sin(x)))),
     sy.exp(sy.sqrt(sy.sin(x))) * (1 / (2 * sy.sqrt(sy.sin(x))) * sy.cos(x))),
    (MathFunction("", 2 ** (3 * x)), 3 * 2 ** (3 * x) * sy.ln(2))])
def test_derivative(expr, result):
    assert expr.derivative() == result


@pytest.mark.parametrize("expression, result", [(MathFunction("", x + y), ValueError),
                                                (MathFunction("", y ** x - 2), ValueError)])
def test_derivative_exceptions(expression, result):
    with pytest.raises(result):
        expression.derivative()


@pytest.mark.parametrize("expr, result", [(MathFunction("", x ** 2, symbols=[x]), {0}),
                                          (MathFunction("", x ** 2 + y ** 2 - 2, symbols=[x, y]),
                                           {-sy.sqrt(2), sy.sqrt(2)}),
                                          (MathFunction("", -11 * x + 22, symbols=[x]), {2}),
                                          (MathFunction("", (x + 76) * (x - 95), symbols=[x]), {95, -76}),
                                          (MathFunction("", -46 / x, symbols=[x]), sy.EmptySet),
                                          (MathFunction("", sy.sqrt((sy.sqrt(x ** 2) - 2) ** 2), symbols=[x]), {2, -2}),
                                          (MathFunction("", (2 ** x), symbols=[x]), sy.EmptySet),
                                          (MathFunction("", sy.ln(x) - 1, symbols=[x]), {sy.exp(1)})])
def test_zeros(expr, result):
    assert expr.zeros() == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", 2 * x - 5), [{2.5}, {-5}]),
                                          (MathFunction("", 1 / x), [sy.EmptySet, {sy.zoo}]),
                                          (MathFunction("", x ** 2 + y ** 2 - 1), [{-1, 1}, {1, -1}]),
                                          (MathFunction("", x ** 2 - 4 * x - 0), [{0, 4}, {0}]),
                                          (MathFunction("", sy.sqrt(x ** 2) - 4), [{-4, 4}, {-4}]),
                                          (MathFunction("", sy.ln(x)), [{1}, {sy.zoo}]),
                                          (MathFunction("", (x - 2) * (4 * x - 4) * (x + 3)), [{2, 1, -3}, {24}]),
                                          (MathFunction("", 1 / (x + 0.5) + 2), [{-1}, {sy.sympify(4.0)}])])
def test_axis_intersection(expr, result):
    assert expr.axis_intersection(x, y) == result[0]
    assert expr.axis_intersection(y, x) == result[1]


@pytest.mark.parametrize("expr, result", [(MathFunction("", sy.cos(x), symbols=[x]), True),
                                          (MathFunction("", x ** 2 + y ** 2 - 1, symbols=[x, y]), True),
                                          (MathFunction("", x + 1, symbols=[x]), False),
                                          (MathFunction("", x ** 2, symbols=[x]), True),
                                          (MathFunction("", sy.sqrt(x ** 2), symbols=[x]), True),
                                          (MathFunction("", sy.ln(x + 1), symbols=[x]), False),
                                          (MathFunction("", sy.ln(sy.sqrt(x ** 2)), symbols=[x]), True)])
def test_is_even(expr, result):
    assert expr.is_even(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", sy.cos(x), symbols=[x]), False),
                                          (MathFunction("", x ** 2 + y ** 2 - 1, symbols=[x, y]), True),
                                          (MathFunction("", x + 1, symbols=[x]), False),
                                          (MathFunction("", x ** 2, symbols=[x]), False),
                                          (MathFunction("", x ** 3, symbols=[x]), True),
                                          (MathFunction("", sy.sqrt(x ** 2), symbols=[x]), False),
                                          (MathFunction("", sy.ln(x + 1), symbols=[x]), False),
                                          (MathFunction("", sy.ln(sy.sqrt(x ** 2)), symbols=[x]), False),
                                          (MathFunction("", sy.sin(x), symbols=[x]), True),
                                          (MathFunction("", 1 / x, symbols=[x]), True),
                                          (MathFunction("", sy.tan(x), symbols=[x]), True),
                                          (MathFunction("", sy.cot(x), symbols=[x]), True),
                                          (MathFunction("", sy.asin(x), symbols=[x]), True)])
def test_is_odd(expr, result):
    assert expr.is_odd(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", 1 / x, symbols=[x]), {0}),
                                          (MathFunction("", sy.ln(x), symbols=[x]), {0}),
                                          (MathFunction("", 1 / (x ** 2), symbols=[x]), {0}),
                                          (MathFunction("", (x ** 2 + 1) / (x - 1), symbols=[x]), {1}),
                                          (MathFunction("", (2 * x ** 2 + 3 * x - 5) / (x * (x - 4)), symbols=[x]),
                                           {0, 4}),
                                          (MathFunction("", (x ** 3) / (3 - x ** 2), symbols=[x]),
                                           {-sy.sqrt(3), sy.sqrt(3)})])
def test_vertical_asymptotes(expr, result):
    assert expr.vertical_asymptotes(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", sy.sqrt(x), symbols=[x]), sy.Interval(0, sy.oo)),
                                          (MathFunction("", sy.sqrt(12 * x + x ** 2), symbols=[x]),
                                           sy.Union(sy.Interval(-sy.oo, -12), sy.Interval(0, sy.oo))),
                                          (MathFunction("", sy.log(x), symbols=[x]),
                                           sy.Interval.open(0, sy.oo)),
                                          (MathFunction("", 1 / x, symbols=[x]),
                                           sy.Union(sy.Interval.open(-sy.oo, 0), sy.Interval.open(0, sy.oo))),
                                          (MathFunction("", sy.sin(x), symbols=[x]), sy.Reals),
                                          (MathFunction("", x, symbols=[x]), sy.Reals),
                                          (MathFunction("", x ** (sy.Number(1) / sy.Number(2)), symbols=[x]),
                                           sy.Interval(0, sy.oo)),
                                          (MathFunction("", x ** 5 + x ** 3 - 10 * x ** 2 + x - 29, symbols=[x]),
                                           sy.Reals)])
def test_domain(expr, result):
    assert expr.domain(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", x ** 2, symbols=[x]), sy.Interval(0, sy.oo)),
                                          (MathFunction("", sy.sin(x), symbols=[x]), sy.Interval(-1, 1)),
                                          (MathFunction("", sy.sqrt(x), symbols=[x]), sy.Interval(0, sy.oo)),
                                          (MathFunction("", sy.log(x), symbols=[x]), sy.Interval(-sy.oo, sy.oo)),
                                          (MathFunction("", 2 ** x, symbols=[x]), sy.Interval.open(0, sy.oo)),
                                          (MathFunction("", sy.atan(x), symbols=[x]),
                                           sy.Interval.open(-sy.pi / 2, sy.pi / 2))])
def test_frange(expr, result):
    assert expr.frange(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", x, symbols=[x]), None),
                                          (MathFunction("", sy.sin(x), symbols=[x]), sy.pi * 2),
                                          (MathFunction("", sy.tan(x), symbols=[x]), sy.pi),
                                          (MathFunction("", sy.atan(x), symbols=[x]), None),
                                          (MathFunction("", sy.sin(x) * x, symbols=[x]), None),
                                          (MathFunction("", sy.log(sy.sin(x)), symbols=[x]), sy.pi * 2),
                                          (MathFunction("", sy.sqrt((sy.sin(x)) ** 2), symbols=[x]), sy.pi),
                                          (MathFunction("", 13 * x ** 0, symbols=[x]), 0)])
def test_periodicity(expr, result):
    assert expr.periodicity(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", 13 * x ** 0, symbols=[x]), True),
                                          (MathFunction("", x ** 2, symbols=[x]), True),
                                          (MathFunction("", x, symbols=[x]), True),
                                          (MathFunction("", x ** 3, symbols=[x]), False),
                                          (MathFunction("", sy.sin(x), symbols=[x]), False),
                                          (MathFunction("", sy.tan(x), symbols=[x]), False),
                                          (MathFunction("", sy.log(x), symbols=[x]), False),
                                          (MathFunction("", sy.asin(x), symbols=[x]), False),
                                          (MathFunction("", sy.sqrt(x ** 2), symbols=[x]), True)
                                          ])
def test_convexity(expr, result):
    assert expr.convexity(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", 13 * x ** 0, symbols=[x]), True),
                                          (MathFunction("", -(x ** 2), symbols=[x]), True),
                                          (MathFunction("", x, symbols=[x]), True),
                                          (MathFunction("", x ** 3, symbols=[x]), False),
                                          (MathFunction("", sy.sin(x), symbols=[x]), False),
                                          (MathFunction("", sy.tan(x), symbols=[x]), False),
                                          (MathFunction("", -sy.log(x), symbols=[x]), False),
                                          (MathFunction("", sy.asin(x), symbols=[x]), False),
                                          (MathFunction("", sy.sqrt(x ** 2), symbols=[x]), True)])
def test_convexity(expr, result):
    assert expr.concavity(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", x, symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", 1 / x, symbols=[x]), {0}),
                                          (MathFunction("", 1 / x + 3, symbols=[x]), {3}),
                                          (MathFunction("", sy.atan(x), symbols=[x]), {-sy.pi / 2, sy.pi / 2}),
                                          (MathFunction("", sy.sin(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.cos(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.cot(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.asin(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.tan(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.log(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", 2 ** x, symbols=[x]), {0}),
                                          (MathFunction("", 4 ** (-x ** 2) + 1, symbols=[x]), {1}),
                                          (MathFunction("", 1 / ((x - 1) * (x + 3)), symbols=[x]), {0})])
def test_horizontal_asymptotes(expr, result):
    assert expr.horizontal_asymptotes(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", sy.sin(x) * x, symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", (2 * x ** 3 + 3 * x + 1) / (2 * x ** 2 + 1), symbols=[x]),
                                           {x}),
                                          (MathFunction("", (x ** 2 + 3) / (x - 1), symbols=[x]), {x + 1}),
                                          (MathFunction("", x * sy.exp(1 / (2 - x)), symbols=[x]), {x - 1}),
                                          (MathFunction("", x, symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", 2 * x ** 0, symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.sqrt(x ** 2 + 1), symbols=[x]), {x, -x}),
                                          (MathFunction("", sy.sin(x), symbols=[x]), {sy.EmptySet}),
                                          (MathFunction("", sy.cos(x), symbols=[x]), {sy.EmptySet})])
def test_slant_asymptotes(expr, result):
    assert expr.slant_asymptotes(*expr.symbols) == result


@pytest.mark.parametrize("expr, result", [(MathFunction("", (x ** 2 + 1) * -1, symbols=[x]), -1),
                                          (MathFunction("", x ** 2, symbols=[x]), sy.oo),
                                          (MathFunction("", sy.sin(x), symbols=[x]), 1),
                                          (MathFunction("", sy.tan(x), symbols=[x]), sy.oo),
                                          (MathFunction("", sy.cos(x), symbols=[x]), 1),
                                          (MathFunction("", x ** 3, symbols=[x]), sy.oo),
                                          (MathFunction("", sy.log(x), symbols=[x]), sy.oo),
                                          (MathFunction("", sy.sqrt(x), symbols=[x]), sy.oo),
                                          (MathFunction("", sy.sqrt(x ** 4), symbols=[x]), sy.oo),
                                          (MathFunction("", sy.Number(4), symbols=[x]), sy.Number(4)),
                                          (MathFunction("", sy.sqrt(sy.sqrt(sy.sqrt(x))), symbols=[x]), sy.oo)])
def test_maximum(expr, result):
    assert expr.maximum(*expr.symbols) == result


@pytest.mark.parametrize("expr, exception", [(MathFunction("", sy.acot(x), symbols=[x]), NotImplementedError),
                                             (MathFunction("", sy.acos(x), symbols=[x]), ValueError),
                                             (MathFunction("", sy.asin(x), symbols=[x]), ValueError)])
def test_maximum_exception(expr, exception):
    with pytest.raises(exception):
        expr.maximum(*expr.symbols)


@pytest.mark.parametrize("expr, result", [(MathFunction("", (x ** 2 + 1) * -1, symbols=[x]), -sy.oo),
                                          (MathFunction("", x ** 2, symbols=[x]), 0),
                                          (MathFunction("", sy.sin(x), symbols=[x]), -1),
                                          (MathFunction("", sy.tan(x), symbols=[x]), -sy.oo),
                                          (MathFunction("", sy.cos(x), symbols=[x]), -1),
                                          (MathFunction("", x ** 3, symbols=[x]), -sy.oo),
                                          (MathFunction("", sy.log(x), symbols=[x]), -sy.oo),
                                          (MathFunction("", sy.sqrt(x), symbols=[x]), 0),
                                          (MathFunction("", sy.sqrt(x ** 4), symbols=[x]), 0),
                                          (MathFunction("", sy.Number(4), symbols=[x]), sy.Number(4)),
                                          (MathFunction("", sy.sqrt(sy.sqrt(sy.sqrt(x))), symbols=[x]), sy.Number(0))])
def test_minimum(expr, result):
    assert expr.minimum(*expr.symbols) == result


@pytest.mark.parametrize("expr, exception", [(MathFunction("", sy.acot(x), symbols=[x]), NotImplementedError),
                                             (MathFunction("", sy.acos(x), symbols=[x]), ValueError),
                                             (MathFunction("", sy.asin(x), symbols=[x]), ValueError)])
def test_minimum_exception(expr, exception):
    with pytest.raises(exception):
        expr.minimum(*expr.symbols)


@pytest.mark.parametrize("expr, result", [(MathFunction("", x ** 2, symbols=[x]), {0}),
                                          (MathFunction("", x, symbols=[x]), sy.EmptySet),
                                          (MathFunction("", x ** 3 - x ** 2, symbols=[x]),
                                           {0, sy.Number(2) / sy.Number(3)}),
                                          (MathFunction("", sy.tan(x), symbols=[x]), sy.EmptySet),
                                          (MathFunction("", sy.log(x), symbols=[x]), sy.EmptySet),
                                          (MathFunction("", 2 ** (x ** 3 - 3 * x ** 2 + 10), symbols=[x]), {0, 2}),
                                          (MathFunction("", sy.sqrt(x ** 2), symbols=[x]), sy.EmptySet),
                                          (MathFunction("", sy.sqrt((x ** 2 - 12) ** 2), symbols=[x]), {0}),
                                          (MathFunction("", 1 / sy.sqrt(sy.tan(x)), symbols=[x]), sy.EmptySet),
                                          (MathFunction("", sy.atan(x ** 3 - x), symbols=[x]),
                                           {-sy.sqrt(3) / 3, sy.sqrt(3) / 3})])
def test_stationary_points(expr, result):
    assert expr.stationary_points(*expr.symbols) == result
