"""
Main core module with bot and logger functionality
"""
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.exceptions import TelegramAPIError
from pymongo import errors

import handling_msg as hmsg
from source.conf.config import Config
from source.core.database import MongoDatabase, no_db_message
from source.extras.custom_logger import setup_logging
from source.extras.status import Status
from source.extras.translation import _
from source.math.graph import Graph
from source.middleware.anti_flood_middleware import ThrottlingMiddleware, rate_limit
from source.middleware.localization_middleware import LanguageMiddleware

# Enable logging
logger = logging.getLogger(__name__)
setup_logging(logger)

# Set up a bot
token: str = Config().properties["APP"]["TOKEN"]
bot: Bot = Bot(token=token)
dispatcher: Dispatcher = Dispatcher(bot, storage=MemoryStorage())

# Init database
mongo = MongoDatabase(logger, bot)

# Set up translator TODO move setup into 'main'
dispatcher.middleware.setup(LanguageMiddleware("Bot", path=Path(__file__).parents[2] / "locales", mongo=mongo))

status_dict = {
    'Derivative': Status.DERIVATIVE,
    'Domain': Status.DOMAIN,
    'Range': Status.RANGE,
    'Zeros': Status.ZEROS,
    'Axes intersection': Status.AXES_INTERSECTION,
    'Periodicity': Status.PERIODICITY,
    'Convexity': Status.CONVEXITY,
    'Concavity': Status.CONCAVITY,
    'Monotonicity': Status.MONOTONICITY,
    'Vertical asymptotes': Status.V_ASYMPTOTES,
    'Horizontal asymptotes': Status.H_ASYMPTOTES,
    'Slant asymptotes': Status.S_ASYMPTOTES,
    'Asymptotes': Status.ASYMPTOTES,
    'Evenness': Status.EVENNESS,
    'Oddness': Status.ODDNESS,
    'Maximum': Status.MAXIMUM,
    'Minimum': Status.MINIMUM,
    'Stationary points': Status.STATIONARY_POINTS
}
"""A dictionary that returns Status by string and string by Status"""
# Adding Status: string matching to status_dict
status_dict.update({value: key.lower() for key, value in status_dict.items()})


@dispatcher.message_handler(commands=["start"])
@rate_limit(limit=1)
async def start(message: types.Message):
    """Send a message when the command /start is issued."""
    user = message.from_user
    await bot.send_message(message.chat.id, _('Hello, {} {}!').format(user.first_name, user.last_name))
    await mongo.go_main(message)


@dispatcher.message_handler(commands=["help"])
@rate_limit(limit=1)
async def chat_help(message: types.Message):
    """Send a message when the command /help is issued."""
    await bot.send_message(message.chat.id, _('Enter:\n/start to restart bot.\n/graph to draw a graph.\n/analyse to '
                                              'go on to investigate the function.'))


@dispatcher.message_handler(commands=["graph"])
@rate_limit(limit=2)
async def graph(message: types.Message):
    """Draw graph, save it as image and send to the user."""
    if message.text == '/graph':
        await mongo.go_graph(message)
    else:
        # await hmsg.send_graph(message)
        asyncio.create_task(hmsg.send_graph(message, ))


@dispatcher.message_handler(commands=["analyse"])
@rate_limit(limit=2)
async def analyse(message: types.Message):
    """Calculate requested function and send result to the user in LaTeX format (or not LaTeX - check config file)"""
    if message.text == '/analyse':
        await mongo.go_analyse(message)
    else:
        await hmsg.send_analyse(message)


@dispatcher.message_handler(commands=["meme"])
@rate_limit(limit=2)
async def meme(message: types.Message):
    """Call meme-api and send random meme from Reddit to user"""
    await hmsg.send_meme(message)


@dispatcher.message_handler(content_types=["text"])
@rate_limit(limit=0.5)
async def default_handler(message: types.Message):
    """Checks user status and direct his message to suitable function."""
    try:
        chat_status = Status(mongo.chat_status_table.find_one({"chat_id": message.chat.id})['status'])
    except errors.PyMongoError:
        await bot.send_message(message.chat.id, _(no_db_message))
        return

    text = message.text
    if chat_status == Status.MAIN:
        if text == _('Draw a graph'):
            await mongo.go_graph(message)
        elif text == _('Analyse function'):
            await mongo.go_analyse(message)
        elif text == _('Get help'):
            await chat_help(message)
        elif text == _('Meme'):
            await meme(message)
            return
        elif text == _('Settings'):
            await mongo.go_settings(message)
        else:
            await message.reply(_('I didn\'t understand what you want'))
    elif chat_status == Status.ANALYSE:
        if text == _('Main menu'):
            await mongo.go_main(message)
        elif text == _('Options'):
            await mongo.go_analyse_menu(message)
        elif text == _('Get help'):
            await bot.send_message(message.chat.id, 'No')  # TODO help
        else:
            await hmsg.send_analyse(message)
    elif chat_status == Status.ANALYSE_MENU:
        if text == _('Back'):
            await mongo.go_analyse(message)
        elif text == _('Main menu'):
            await mongo.go_main(message)
        else:
            try:
                status_dict_translated = {_(k): v for k, v in status_dict.items()}
                await mongo.go_analyse_option(message, status_dict_translated[message.text])
            except KeyError:
                await hmsg.send_analyse(message)
    elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
        if text == _('Back'):
            await mongo.go_analyse_menu(message)
        elif text == _('Main menu'):
            await mongo.go_main(message)
        else:
            message.text = f'{status_dict[chat_status]} {message.text.lower()}'
            await hmsg.send_analyse(message)
            await bot.send_message(message.chat.id, _("Enter a function to explore or go back"))
    elif chat_status == Status.GRAPH:
        if text == _('Main menu'):
            await mongo.go_main(message)
        else:
            await hmsg.send_graph(message)
            await bot.send_message(message.chat.id, _("Enter a function you want to draw or go to the main menu"))
    elif chat_status == Status.SETTINGS:
        logger.debug(message.text)
        try:
            if text == _('Main menu'):
                await mongo.go_main(message)
                return
            if text in [on := _('On meme'), _('Off meme')]:
                await mongo.set_meme(message, text == on)
            elif text in [_('Set en language'), _('Set ru language')]:
                language = text.split()[1]
                await mongo.set_language(message, language)
            else:
                await message.reply(_('I didn\'t understand what you want'))
                return
        except errors.PyMongoError:
            await bot.send_message(message.chat.id, _(no_db_message))
        await bot.send_message(message.chat.id, _("Settings saved"))
        await mongo.go_settings(message)


@dispatcher.errors_handler()
def error(update: types.Update, exception: TelegramAPIError):
    """Log Errors caused by Updates."""
    logger.error('Update %s\nCaused error %s', update, exception)


if __name__ == '__main__':
    Graph.setup_plot_style()
    logger.info('Bot is started')
    dispatcher.middleware.setup(LoggingMiddleware(logger=logger))
    dispatcher.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dispatcher, skip_updates=True)
