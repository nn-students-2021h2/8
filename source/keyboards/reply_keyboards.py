from aiogram.types import ReplyKeyboardMarkup

from source.extras.translation import _


async def go_main_markup(meme_is_active: bool) -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(_("Draw graph"))
    reply_markup.add(_("Analyse function"))
    reply_markup.add(_("Settings"))
    reply_markup.add(_("Get help"))
    if meme_is_active:
        reply_markup.add(_("Meme"))
    return reply_markup


async def go_settings_markup(user_settings) -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(_("Set {} language").format('ru' if user_settings['lang'] == 'en' else 'en'))
    reply_markup.add(_("{} meme button").format(_('Off') if user_settings['meme'] else _('On')))
    reply_markup.add(_("Main menu"))
    return reply_markup


async def go_graph_markup() -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(_("Main menu"))
    reply_markup.add(_("Examples"))
    return reply_markup


async def go_analyse_markup() -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(_("Options"))
    reply_markup.add(_("Examples"))
    reply_markup.add(_("Main menu"))
    return reply_markup


async def go_analyse_menu_markup() -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(_('Derivative'), _('Domain'), _('Range'))
    reply_markup.add(_('Stationary points'), _('Periodicity'), _('Monotonicity'))
    reply_markup.add(_('Convexity'), _('Concavity'), _('Asymptotes'))
    reply_markup.add(_('Vertical asymptotes'), _('Slant asymptotes'), _('Horizontal asymptotes'))
    reply_markup.add(_('Oddness'), _('Axes intersection'), _('Evenness'))
    reply_markup.add(_('Maximum'), _('Minimum'), _('Zeros'))
    reply_markup.add(_('Main menu'), _('Back'))
    return reply_markup


async def go_analyse_option() -> ReplyKeyboardMarkup:
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(_("Back"))
    reply_markup.add(_("Main menu"))
    return reply_markup


