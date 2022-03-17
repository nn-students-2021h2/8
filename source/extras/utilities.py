"""Store common and general functions to use in any place of code"""
import asyncio
import functools
import sympy as sy
from io import BytesIO
from PIL import Image, ImageOps

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
