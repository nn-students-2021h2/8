import matplotlib.pyplot as plt
import numpy as np
import sympy

filename = 'graph.png'

def work(text):
    y = lambda x: np.sqrt(x)
    fig = plt.subplots()
    x = np.linspace(0, 100, 20)
    plt.plot(x, y(x))
    plt.savefig(filename)
    return filename
