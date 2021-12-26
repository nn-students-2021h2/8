import matplotlib.pyplot as plt
import numpy as np
from telegram import Update
from telegram.ext import CallbackContext

from graph import Graph
from parser import Parser, ParseError

FILE_NAME = 'graph.png'

def work(text):
    y = lambda x: np.sqrt(x)
    fig = plt.subplots()
    x = np.linspace(0, 100, 20)
    plt.plot(x, y(x))
    plt.savefig(FILE_NAME)
    return FILE_NAME


def send_graph(update: Update, context: CallbackContext):
    user = update.message.from_user
    expr = " ".join(context.args)

    parser = Parser()
    try:
        tokens = parser.parse(expr)
        Graph.draw(tokens, FILE_NAME)
    except ParseError as err:
        update.message.reply_text(str(err))
        return

    with open(FILE_NAME, 'rb') as graph_file:
        context.bot.sendPhoto(
            chat_id=user['id'],
            photo=graph_file,
            caption='Here a graph of requested functions'
        )
