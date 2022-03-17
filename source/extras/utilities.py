"""Store common and general functions to use in any place of code"""
import asyncio
import functools
import sympy as sy
from io import BytesIO
from PIL import Image, ImageOps
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import source.math.help_functions as hlp

# A number of dots per inch for TeX pictures
DPI = '500'


def run_asynchronously(f):
    """Run function in executor letting the function be performed asynchronously"""

    @functools.wraps(f)
    def decorator(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return decorator


@run_asynchronously
def run_TeX(latex: str, result_picture: BytesIO):
    """
        Asynchronously render a picture using TeX distribution
        :param latex: latex text to compile
        :param result_picture: rendered picture
        """
    preamble = r"""\documentclass[varwidth,12pt]{standalone}
        \usepackage{euler} \usepackage{amsmath} \usepackage{amsfonts} \usepackage[russian]{babel}
        \begin{document}"""
    sy.preview(fr'${latex}$', output='png', preamble=preamble,
               viewer='BytesIO', outputbuffer=result_picture, dvioptions=['-D', DPI])


@run_asynchronously
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


async def reply_markup_analysis(in_analysis: bool):
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.analysis_examples()
    for i in range(10):
        reply_markup.add(InlineKeyboardButton(ex[i][len('/analyse '):] if in_analysis else ex[i],
                                              callback_data=f'example_analysis_{i}'))
    return reply_markup


async def reply_markup_graph(in_graph: bool):
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.graph_examples()
    for i in range(10):
        reply_markup.add(InlineKeyboardButton(ex[i][len('/graph '):] if in_graph else ex[i],
                                              callback_data=f'example_graph_{i}'))
    return reply_markup
