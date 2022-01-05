"""
In this module we process events related to bot (such as messages, requests)
"""

from telegram import Update
from telegram.ext import CallbackContext

from graph import Graph
from parser import Parser, ParseError

FILE_NAME = 'graph.png'


def echo(text: str):
    """On simple messages bot replies with echo"""
    return text + '!'


def send_graph(update: Update, context: CallbackContext):
    """User requested to draw a plot"""
    user = update.message.from_user
    expr = " ".join(context.args)
    parser = Parser()

    try:
        tokens = parser.parse(expr)
        graph = Graph(FILE_NAME)
        graph.draw(tokens)
    except ParseError as err:
        update.message.reply_text(str(err))
        return

    with open(FILE_NAME, 'rb') as graph_file:
        output_message = "Here a graph of requested functions"
        if warning := parser.pop_last_warning():
            output_message += f"\n{warning}"

        context.bot.sendPhoto(
            chat_id=user['id'],
            photo=graph_file,
            caption=output_message
        )
