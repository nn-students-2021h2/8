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
    def __init__(self):
        self.tokens = {'range': [], 'explicit': [], 'implicit': [], 'unknown': []}

    def _check_range(self, token):
        if (token.strip().find("from")) == 0:
            definition_area = token.split()
            # if 'from _ to _' construction doesn't contain four words, that it is syntax error
            if len(definition_area) != 4:
                raise ParseError(f"Mistake in function range parameters.\nYour input: {token.strip()}\n"
                                 "Please, check your \"from _ to _\" statement.")

            try:
                left = float(definition_area[1])
                right = float(definition_area[3])
            except ValueError:
                raise ParseError(f"Mistake in function range parameters.\nYour input: {token.strip()}\n"
                                 "Please, check your \"from _ to _\" statement.")
            self.tokens['range'] = [left, right]
            return True

        return False

    @staticmethod
    def _check_function(token):
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
                    raise ValueError("Mistake in implicit function: Found more than 2 equals.\n"
                                     f"Your input: {token.strip()}\n"
                                     "Please, check your math formula")
            except SympifyError:
                raise ParseError(f"Mistake in expression.\nYour input: {token.strip()}\n"
                                 "Please, check your math formula.")
        return foo

    def parse(self, expr):
        x, y = sy.symbols('x y')
        parts = expr.split(',')

        for token in parts:
            # If it is a function range
            try:
                if self._check_range(token):
                    continue
            except ParseError as err:
                raise err

            # If it is a function
            try:
                foo = self._check_function(token)
            except ParseError as err:
                raise err

            # Update tokens list
            variables_count = len(foo.free_symbols)
            if variables_count <= 1:
                # If it is an explicit function
                graph = Graph(token.strip(), foo, 'explicit', list(foo.free_symbols))
                self.tokens['explicit'].append(graph)
            elif variables_count == 2:
                # If it is an implicit function
                graph = Graph(token.strip(), foo, 'implicit', list(foo.free_symbols))
                self.tokens['implicit'].append(graph)
            elif variables_count > 2:
                # If it is an unknown expression
                self.tokens['unknown'].append(token)

        return self.tokens
