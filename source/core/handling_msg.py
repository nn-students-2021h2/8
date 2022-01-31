"""
In this module we process events related to bot (such as messages, requests)
"""
from pathlib import Path

from telegram import Update
from telegram.ext import CallbackContext

from source.math.graph import Graph
from source.math.parser import Parser, ParseError


def echo(text: str):
    """On simple messages bot replies with echo"""
    return text + '!'


def send_graph(update: Update, context: CallbackContext):
    """User requested to draw a plot"""
    user = update.message.from_user
    resources_path = Path(__file__).resolve().parents[2] / "resources"
    file_path = resources_path / f"{user['id']}.png"
    if context.args:
        expr = " ".join(context.args)
    else:
        expr = update.message.text.lower()
    parser = Parser()

    try:
        tokens = parser.parse(expr)
        graph = Graph(file_path)
        graph.draw(tokens)
    except ParseError as err:
        update.message.reply_text(str(err))
        return

    with open(file_path, 'rb') as graph_file:
        output_message = "Here a graph of requested functions"
        if warning := parser.pop_last_warning():
            output_message += f"\n{warning}"

        context.bot.sendPhoto(
            chat_id=user['id'],
            photo=graph_file,
            caption=output_message
        )
