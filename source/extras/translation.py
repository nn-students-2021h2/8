"""
File with gettext alias
"""
from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware

i18n = I18nMiddleware("Bot", Path(__file__).parents[2] / "locales")
_ = i18n.gettext
__ = i18n.gettext

graph_guide_texts = [_("""
*General information:*
Our bot knows how to draw graphs based on a given expression, with the ability to specify \
parameters such as area of definition (domain), area of value (range), and aspect ratio.

If you don't want to read the tons of words, you can use the "Examples" button to figure out \
for yourself how the bot works.

You can use buttons to interact with the bot, or you can use commands that work everywhere and always.
"""), _("""
*Quick start:* 
`/graph function1, function2, ..., parameter1, parameter2, ...` — draws the functions f(x) or y = f(x), or \
f(x, y) = const on a single graph with the given parameters listed separated by commas. \
Functions are given in mathematical form. Sometimes functions can have brackets and multiplication omitted. Example:
`/graph y = 2x, x^2 + y^2 = 16, sin x, sqrt x, x = (-20, 20), y = (-10, 10)`

The bot may not always accurately draw the graph or define its area of definition and range, so you can \
specify them manually via parameters.
"""), _("""*Parameters:*
— `Domain` — you can specify the values of the argument (the 'x' variable), for example:
`x from -5 to 10, x in [0, 24.5], for x = (10, 20)`, etc.

— `Range` — you can specify the values of the function (variable 'y') in the same way as the area of definition, \
for example:
`for y from -5 to 0, y in (0, 1.2), y=(10, 20)`, etc.

— `Aspect ratio` — it is allowed to set the ratio of the chart's width to its height, for example:
`aspect ratio = 1, ratio=1, ratio = 0.5` и т.д. Can be useful for drawing circles.
""")]

analysis_guide_texts = [_("""
*General information:*
Our bot knows how to analyse functions by a query written in English.

If you don't want to read the tons of words, you can use the "Examples" button to figure out \
for yourself how the bot works.

You can use buttons to interact with the bot, or you can use commands that work everywhere and always.
"""), _("""
*Quick start:*
`/analyse option` —  tries to understand the query and output an answer for the function specified in the query.
Queries have their own patterns, but in general natural English is implied. The function must be in mathematical form. \
Sometimes functions can have brackets and multiplication omitted. Examples:
`/analyse domain of 2 sqrt x`
`/analyse diff 2 a^4 b c^2 by b, a`
`/analyse is function sin 4x even?`
etc.

Due to the fact that it is quite difficult to give an exact answer to any problem, the bot may make a mistake or not \
even solve the problem. Be tolerant of the handicapped.

See "Examples" for clarity.
"""), _("""
*Options:*
Available options for function analysis. Some words can be abbreviated or replaced with synonyms - the bot will \
try to understand you:
- Derivative
- Domain
- Range
- Function zeros
- Intersection with axes
- Periodicity
- Convexity
- Concavity
- Vertical asymptotes
- Horizontal asymptotes
- Slant asymptotes
- All Asymptotes
- Evenness
- oddness
- Maximum
- Minimum
- Critical points
- Monotonicity
""")]
