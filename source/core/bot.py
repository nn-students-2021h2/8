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
from source.extras.custom_logger import setup_logging
from source.math.graph import Graph
from source.middleware.anti_flood_middleware import ThrottlingMiddleware, rate_limit
from source.middleware.localization_middleware import LanguageMiddleware
from source.core.database import MongoDatabase, no_db_message
from source.extras.status import Status


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
_ = i18n = dispatcher.middleware.setup(LanguageMiddleware("Bot", path=Path(__file__).parents[2] / "locales", mongo=mongo))


status_dict = {
    'Derivative': Status.DERIVATIVE,
    'Domain': Status.DOMAIN,
    'Range': Status.RANGE,
    'Zeros': Status.ZEROS,
    'Axes intersection': Status.AXES_INTERSECTION,
    'Periodicity': Status.PERIODICITY,
    'Convexity': Status.CONVEXITY,
    'Concavity': Status.CONCAVITY,
    'Continuity': Status.CONTINUITY,
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
    await bot.send_message(message.chat.id, _('Enter:\n/start to restart bot.\n/graph to draw graph.\n/analyse to '
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
    if chat_status == Status.MAIN:
        match message.text:
            case 'Draw graph':
                await mongo.go_graph(message)
            case 'Analyse function':
                await mongo.go_analyse(message)
            case 'Get help':
                await chat_help(message)
            case 'Meme':
                await meme(message)
                return
            case 'Settings':
                await mongo.go_settings(message)
            case _:
                await message.reply(_('I didn\'t understand what you want'))
    elif chat_status == Status.ANALYSE:
        match message.text:
            case 'Main menu':
                await mongo.go_main(message)
            case 'Options':
                await mongo.go_analyse_menu(message)
            case 'Get help':
                await bot.send_message(message.chat.id, 'No')
            case _:
                await hmsg.send_analyse(message)
    elif chat_status == Status.ANALYSE_MENU:
        match message.text:
            case 'Back':
                await mongo.go_analyse(message)
            case 'Main menu':
                await mongo.go_main(message)
            case _:
                try:
                    await mongo.go_analyse_option(message, status_dict[message.text])
                except KeyError:
                    await hmsg.send_analyse(message)
    elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
        match message.text:
            case 'Back':
                await mongo.go_analyse_menu(message)
            case 'Main menu':
                await mongo.go_main(message)
            case _:
                message.text = f'{status_dict[chat_status]} {message.text.lower()}'
                await hmsg.send_analyse(message)
                await bot.send_message(message.chat.id, _("Enter function to explore or go back"))
    elif chat_status == Status.GRAPH:
        match message.text:
            case 'Main menu':
                await mongo.go_main(message)
            case _:
                await hmsg.send_graph(message)
                await bot.send_message(message.chat.id, _("Enter function you want to draw or go to the main menu"))
    elif chat_status == Status.SETTINGS:
        logger.debug(message.text)
        try:
            match message.text:
                case 'Main menu':
                    await mongo.go_main(message)
                    return
                case 'On meme':
                    mongo.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"meme": True}})
                case 'Off meme':
                    mongo.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"meme": False}})
                case 'Set en language':
                    mongo.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"lang": 'en'}})
                case 'Set ru language':
                    mongo.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"lang": 'ru'}})
                case _:
                    await message.reply(_('I didn\'t understand what you want'))
                    return
        except errors.PyMongoError:
            await bot.send_message(message.chat.id, _(no_db_message))
        await bot.send_message(message.chat.id, "New settings saved")
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
