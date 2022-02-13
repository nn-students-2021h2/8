"""
In this module we process events related to bot (such as messages, requests)
"""
from io import BytesIO
from pathlib import Path

import sympy as sy
import telegram
from PIL import Image, ImageOps
from telegram import Update
from telegram.ext import CallbackContext

from source.conf import Config
from source.math.calculus_parser import CalculusParser
from source.math.graph import Graph, DrawError
from source.math.graph_parser import GraphParser, ParseError

# We get "USE_LATEX" parameter from settings
SETTINGS = Config()

# A number of dots per inch for TeX pictures
DPI = '600'


def resize_image(image_to_resize: BytesIO, output_buffer: BytesIO):
    """
    Resize image to fit in the Telegram window and add a frame
    :param image_to_resize: a BytesIO object containing the image you want to resize
    :param output_buffer: result image buffer
    """
    image_to_resize.seek(0)
    output_buffer.seek(0)

    image = Image.open(BytesIO(image_to_resize.read()))
    height, width = image.size
    max_size = 10000

    # Resize to max size
    if height > max_size or width > max_size:
        ratio = min(max_size / height, max_size / width)
        image.thumbnail((int(height * ratio), int(width * ratio)))

    # Set borders
    # noinspection PyTypeChecker
    ImageOps.expand(image, border=100, fill="white").save(output_buffer, format="PNG")
    output_buffer.seek(0)


def echo(text: str):
    """On simple messages bot replies that didn't understand user"""
    return 'I didn\'t understand what you want'


def send_graph(update: Update, context: CallbackContext):
    """User requested to draw a plot"""
    user = update.message.from_user
    resources_path = Path(__file__).resolve().parents[2] / "resources"
    file_path = resources_path / f"{user['id']}.png"
    if context.args:
        expr = " ".join(context.args).lower()
    else:
        expr = update.message.text.lower()

    parser = GraphParser()
    try:
        parser.parse(expr)
        graph = Graph(file_path)
        graph.draw(parser.tokens)
    except (ParseError, DrawError) as err:
        update.message.reply_text(str(err))
        return

    with open(file_path, 'rb') as graph_file:
        output_message = "Here a graph of requested functions"
        context.bot.send_photo(
            chat_id=user['id'],
            photo=graph_file,
            caption=output_message + '\n' + "\n".join(parser.warnings)
        )
    parser.clear_warnings()


def send_analyse(update: Update, context: CallbackContext):
    """User requested some function analysis"""
    user = update.message.from_user
    if context.args:
        expr = " ".join(context.args).lower()
    else:
        expr = update.message.text.lower()
    parser = CalculusParser()
    try:
        # Parse request and check if some template was found
        # If parser can't understand what user mean, it returns False
        is_pattern_found = parser.parse(expr)
        if not is_pattern_found:
            update.message.reply_text("Couldn't find a suitable template. Check the input.")
            return
        result = parser.process_query()

        # If USE_LATEX set in True, then send picture to the user. Else, send basic text
        if SETTINGS.properties["APP"]["USE_LATEX"]:
            latex = parser.make_latex(result)
            with BytesIO() as latex_picture, BytesIO() as resized_image:
                sy.preview(fr'${latex}$', output='png', viewer='BytesIO', outputbuffer=latex_picture,
                           dvioptions=['-D', DPI])

                resize_image(latex_picture, resized_image)

                # If we can't send photo due to Telegram limitations, then send image as file instead
                try:
                    context.bot.send_photo(
                        chat_id=user['id'],
                        photo=resized_image,
                        caption="\n".join(parser.warnings)
                    )
                except telegram.error.BadRequest:
                    parser.push_warning("Photo size is too large, therefore I send you a file.")
                    context.bot.send_document(
                        chat_id=user['id'],
                        document=resized_image,
                        caption="\n".join(parser.warnings)
                    )
        else:
            context.bot.send_message(
                chat_id=user['id'],
                text=str(result)
            )
        parser.clear_warnings()
    except RecursionError:
        update.message.reply_text("Incorrect input. Please check your function.")
    except (ParseError, ValueError, NotImplementedError) as err:
        update.message.reply_text(str(err))
