import matplotlib.pyplot as plt
import numpy as np

from telegram import Update
from telegram.ext import CallbackContext

from graph import Graph, DrawException

filename = 'graph.png'


def work(text):
    y = lambda x: np.sqrt(x)
    fig = plt.subplots()
    x = np.linspace(0, 100, 20)
    plt.plot(x, y(x))
    plt.savefig(filename)
    return filename


def send_graph(update: Update, context: CallbackContext):
    user = update.message.from_user
    gr = Graph(context.args, filename)
    try:
        gr.draw()
    except DrawException:
        update.message.reply_text('Check your input again')
        return

    with open(gr.get_file_path(), 'rb') as graph_file:
        context.bot.sendPhoto(
            chat_id=user['id'],
            photo=graph_file,
            caption=f'Here a graph of function \'{str(gr)}\''
        )
