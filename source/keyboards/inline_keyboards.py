from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from source.extras.translation import _
import source.math.help_functions as hlp


async def chat_help_markup() -> InlineKeyboardMarkup:
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(InlineKeyboardButton(_("Graph guide"), callback_data='graph_guide'))
    reply_markup.add(InlineKeyboardButton(_("Graph examples"), callback_data='graph_examples'))
    reply_markup.add(InlineKeyboardButton(_("Analysis guide"), callback_data='analysis_guide'))
    reply_markup.add(InlineKeyboardButton(_("Analysis examples"), callback_data='analysis_examples'))
    return reply_markup


async def reply_markup_analysis(in_analysis: bool) -> InlineKeyboardMarkup:
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.analysis_examples()
    for i in range(len(ex)):
        reply_markup.add(InlineKeyboardButton(ex[i] if in_analysis else '/analyse ' + ex[i],
                                              callback_data=f'example_analysis_{i}'))
    return reply_markup


async def reply_markup_graph(in_graph: bool) -> InlineKeyboardMarkup:
    reply_markup = InlineKeyboardMarkup()
    ex = hlp.graph_examples()
    for i in range(len(ex)):
        reply_markup.add(InlineKeyboardButton(ex[i] if in_graph else '/graph ' + ex[i],
                                              callback_data=f'example_graph_{i}'))
    return reply_markup
