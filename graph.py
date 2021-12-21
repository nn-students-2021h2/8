import sympy as sy
from sympy.plotting import plot


# This exception raise when sympy cannot draw a function plot
class DrawException(Exception):
    pass


# The class represents a plot of function with attributes 'tokens' - list of string arguments, that can be converted
# into math expression; 'file_path' - path to the file that use as temporary plot storage.
class Graph:
    def __init__(self, tokens, file_path='last_image.png'):
        self._tokens = tokens
        self._file_path = file_path

    def __str__(self):
        return ''.join(self._tokens)

    # Parse tokens and save plot in file 'self.file_path'
    def draw(self):
        expression = str(self)

        try:
            p1 = plot(sy.sympify(expression), show=False)
        except (IndexError, ValueError, TypeError):
            raise DrawException

        p1.save(self._file_path)

    def set_file_path(self, new_file_path):
        self._file_path = new_file_path

    def get_file_path(self):
        return self._file_path
