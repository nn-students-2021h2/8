import sympy as sy

# This exception raise when sympy cannot draw a function plot
from sympy import SympifyError
from graph import Graph

class ParseError(Exception):
    pass

# Foo Range
# Explicit foo
# Implicit foo
class Parser:
    tokens = {'range': [], 'explicit': [], 'implicit': [], 'unknown': []}

    def __init__(self):
        pass

    def parse(self, expr):
        x, y = sy.symbols('x y')
        parts = expr.split(',')

        for token in parts:
            # if it is a function range
            if (index := token.find("from")) != -1:
                definition_area = token[index:].split()[:4]
                try:
                    left = float(definition_area[1]) # TODO try
                    right = float(definition_area[3])
                except ValueError:
                    raise ParseError(f"Mistake in function range parameters.\nYour input: {token.strip()}\n"
                                         "Please, check your \"from _ to _\" statement.")
                self.tokens['range'] = [left, right]
                continue

            # if it is a function
            try:
                foo = sy.simplify(token)
            except ValueError:
                expr_parts = token.split('=')
                parts_count = len(expr_parts)

                try:
                    if parts_count == 1:
                        foo = sy.Eq(sy.simplify(expr_parts[0]))
                    elif parts_count == 2:
                        foo = sy.Eq(sy.simplify(expr_parts[0]), sy.simplify(expr_parts[1]))
                    else:
                        raise ValueError("asdasdasd")
                except SympifyError:
                    raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                                         "Please, check your math formula.")

            # update tokens list
            variable_count = len(foo.free_symbols)
            if variable_count <= 1:
                # if it is an explicit function
                graph = Graph(token.strip(), foo, 'implicit', list(foo.free_symbols))
                self.tokens['implicit'].append(graph)
            elif variable_count == 2:
                # if it is an implicit function
                graph = Graph(token.strip(), foo, 'explicit', list(foo.free_symbols))
                self.tokens['explicit'].append(graph)
            elif variable_count > 2:
                # if it is an unknown expression
                self.tokens['unknown'].append(token)

        return self.tokens
