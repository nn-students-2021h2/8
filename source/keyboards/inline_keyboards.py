"""Module with inline keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from source.extras.translation import _
import source.math.help_functions as hlp


async def chat_help_markup() -> InlineKeyboardMarkup:
    """Chat help keyboard"""
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(InlineKeyboardButton(_("Graph guide"), callback_data='graph_guide'))
    reply_markup.add(InlineKeyboardButton(_("Graph examples"), callback_data='graph_examples'))
    reply_markup.add(InlineKeyboardButton(_("Analysis guide"), callback_data='analysis_guide'))
    reply_markup.add(InlineKeyboardButton(_("Analysis examples"), callback_data='analysis_examples'))
    reply_markup.add(InlineKeyboardButton("Github",
                                          url='https://github.com/nn-students-2021h2/Function_explorer_bot_8'))
    return reply_markup


async def reply_markup_analysis(in_analysis: bool) -> InlineKeyboardMarkup:
    """Analysis examples keyboard"""
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.analysis_examples()
    for i, example in enumerate(ex):
        reply_markup.add(InlineKeyboardButton(example if in_analysis else '/analyse ' + example,
                                              callback_data=f'example_analysis_{i}'))
    return reply_markup


async def reply_markup_graph(in_graph: bool) -> InlineKeyboardMarkup:
    """Graph examples keyboard"""
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.graph_examples()
    for i, example in enumerate(ex):
        reply_markup.add(InlineKeyboardButton(example if in_graph else '/graph ' + example,
                                              callback_data=f'example_graph_{i}'))
    return reply_markup
