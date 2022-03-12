"""
Main core module with bot and logger functionality
"""
import asyncio
import logging
from enum import Enum
from functools import total_ordering

import pymongo.collection
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.exceptions import TelegramAPIError
from pymongo import MongoClient, errors

import handling_msg as hmsg
from source.conf.config import Config
from source.conf.custom_logger import setup_logging
from source.math.graph import Graph
from source.middleware.anti_flood_middleware import ThrottlingMiddleware, rate_limit

# Enable logging
logger = logging.getLogger(__name__)
setup_logging(logger)

# Set up a bot
token = Config().properties["APP"]["TOKEN"]
bot: Bot = Bot(token=token)
dispatcher: Dispatcher = Dispatcher(bot, storage=MemoryStorage())


@total_ordering
class Status(Enum):
    """Enum for define statuses of chat"""
    MAIN = 0
    GRAPH = 1
    ANALYSE = 2
    DERIVATIVE = 3
    DOMAIN = 4
    RANGE = 5
    ZEROS = 6
    AXES_INTERSECTION = 7
    PERIODICITY = 8
    CONVEXITY = 9
    CONCAVITY = 10
    CONTINUITY = 11
    V_ASYMPTOTES = 12
    H_ASYMPTOTES = 13
    S_ASYMPTOTES = 14
    ASYMPTOTES = 15
    EVENNESS = 16
    ODDNESS = 17
    MAXIMUM = 18
    MINIMUM = 19
    STATIONARY_POINTS = 20
    ANALYSE_MENU = 21
    SETTINGS = 22

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


no_db_message = "There were problems, the functionality is limited.\nYou can only use the bot with commands."

chat_status_table: pymongo.collection.Collection
"""Collection that returns the Status of user by chat id"""


def init_pymongo_db():
    """Initialise connection to mongo database"""
    global chat_status_table
    conf = Config()
    client = MongoClient(conf.properties["DB_PARAMS"]["ip"], conf.properties["DB_PARAMS"]["port"],
                         serverSelectionTimeoutMS=5000)
    try:
        logger.info(client.server_info())
    except errors.PyMongoError:
        logger.critical("Unable to connect to the MongoDB server.")
    db = client[conf.properties["DB_PARAMS"]["database_name"]]
    chat_status_table = db["chat_status"]
    chat_status_table.create_index("chat_id", unique=True)


async def change_user_status(message: types.Message, status: Status) -> int:
    """Update user status in mongo database. It returns 1 if the connection is lost and 0 if all ok"""
    try:
        if chat_status_table.find_one({"chat_id": message.chat.id}) is None:
            chat_status_table.insert_one({"chat_id": message.chat.id, "status": status.value, "lang":"en", "meme": False})
        else:
            chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"status": status.value}})
        return 0
    except errors.PyMongoError:
        await bot.send_message(message.chat.id, no_db_message)
        return 1


async def go_main(message: types.Message):
    """Change status of user and send main menu to user."""
    if await change_user_status(message, Status.MAIN):
        return
    try:
        meme_is_active = chat_status_table.find_one({"chat_id": message.chat.id})['meme']
    except errors.PyMongoError:
        await bot.send_message(message.chat.id, no_db_message)
        return
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Draw graph")
    reply_markup.add("Analyse function")
    reply_markup.add("Settings")
    reply_markup.add("Get help")
    if meme_is_active:
        reply_markup.add("Meme")
    await bot.send_message(message.chat.id, 'Choose action', reply_markup=reply_markup)


async def go_settings(message: types.Message):
    """Change status of user and send settings menu to user."""
    if await change_user_status(message, Status.SETTINGS):
        return
    try:
        user_settings = chat_status_table.find_one({"chat_id": message.chat.id})
    except errors.PyMongoError:
        await bot.send_message(message.chat.id, no_db_message)
        return
    await bot.send_message(message.chat.id, f"Your settings\nLanguage: {user_settings['lang']}\nMeme: {'on' if user_settings['meme'] else 'off'}")
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(f"Set {'ru' if user_settings['lang'] == 'en' else 'en'} language")
    reply_markup.add(f"{'Off' if user_settings['meme'] else 'On'} meme")
    reply_markup.add("Main menu")
    await bot.send_message(message.chat.id, "Choose changes that you want.", reply_markup=reply_markup)


async def go_graph(message: types.Message):
    """Change status of user and send draw graph menu to user."""
    if await change_user_status(message, Status.GRAPH):
        return
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Main menu")
    await bot.send_message(message.chat.id, "Enter function to draw or go to main menu", reply_markup=reply_markup)


async def go_analyse(message: types.Message):
    """Change status of user to 'analyse' and send analyse menu"""
    if await change_user_status(message, Status.ANALYSE):
        return
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Options")
    reply_markup.add("Get help")
    reply_markup.add("Main menu")
    await bot.send_message(message.chat.id, "Choose option or enter command or go to main menu",
                           reply_markup=reply_markup)


async def go_analyse_menu(message: types.Message):
    """Change status of user to 'analyze menu' and send options to analyze menu'"""
    if await change_user_status(message, Status.ANALYSE_MENU):
        return
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add('Derivative', 'Domain', 'Range',
                                                                 'Stationary points', 'Periodicity',
                                                                 'Continuity', 'Convexity', 'Concavity',
                                                                 'Horizontal asymptotes', 'Vertical asymptotes',
                                                                 'Asymptotes', 'Evenness', 'Oddness',
                                                                 'Axes intersection', 'Slant asymptotes',
                                                                 'Maximum', 'Minimum', 'Zeros',
                                                                 'Main menu', 'Back')
    await bot.send_message(message.chat.id, "Choose option to analyze or go back", reply_markup=reply_markup)


async def go_analyse_option(message: types.Message, option: Status):
    """Change status of user to option and send 'go back' menu'"""
    if await change_user_status(message, option):
        return
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Back")
    reply_markup.add("Main menu")
    await bot.send_message(message.chat.id, "Enter function to analyse or go back", reply_markup=reply_markup)


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
    await bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name} {message.from_user.last_name}!')
    await go_main(message)


@dispatcher.message_handler(commands=["help"])
@rate_limit(limit=1)
async def chat_help(message: types.Message):
    """Send a message when the command /help is issued."""
    await bot.send_message(message.chat.id, 'Enter:\n/start to restart bot.\n/graph to draw graph.\n/analyse to '
                                            'go on to investigate the function.\n/meme to get random meme from reddit.')


@dispatcher.message_handler(commands=["graph"])
@rate_limit(limit=2)
async def graph(message: types.Message):
    """Draw graph, save it as image and send to the user."""
    if message.text == '/graph':
        await go_graph(message)
    else:
        # await hmsg.send_graph(message)
        asyncio.create_task(hmsg.send_graph(message, ))


@dispatcher.message_handler(commands=["analyse"])
@rate_limit(limit=2)
async def analyse(message: types.Message):
    """Calculate requested function and send result to the user in LaTeX format (or not LaTeX - check config file)"""
    if message.text == '/analyse':
        await go_analyse(message)
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
        chat_status = Status(chat_status_table.find_one({"chat_id": message.chat.id})['status'])
    except errors.PyMongoError:
        await bot.send_message(message.chat.id, no_db_message)
        return
    if message.text == 'Meme':
        await meme(message)
        return
    if chat_status == Status.MAIN:
        match message.text:
            case 'Draw graph':
                await go_graph(message)
            case 'Analyse function':
                await go_analyse(message)
            case 'Get help':
                await chat_help(message)
            case 'Settings':
                await go_settings(message)
            case _:
                await message.reply(hmsg.echo())
    elif chat_status == Status.ANALYSE:
        match message.text:
            case 'Main menu':
                await go_main(message)
            case 'Options':
                await go_analyse_menu(message)
            case 'Get help':
                await bot.send_message(message.chat.id, 'No')
            case _:
                await hmsg.send_analyse(message)
    elif chat_status == Status.ANALYSE_MENU:
        match message.text:
            case 'Back':
                await go_analyse(message)
            case 'Main menu':
                await go_main(message)
            case _:
                try:
                    await go_analyse_option(message, status_dict[message.text])
                except KeyError:
                    await hmsg.send_analyse(message)
    elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
        match message.text:
            case 'Back':
                await go_analyse_menu(message)
            case 'Main menu':
                await go_main(message)
            case _:
                message.text = f'{status_dict[chat_status]} {message.text.lower()}'
                await hmsg.send_analyse(message)
                await bot.send_message(message.chat.id, "Enter function to explore or go back")
    elif chat_status == Status.GRAPH:
        match message.text:
            case 'Main menu':
                await go_main(message)
            case _:
                await hmsg.send_graph(message)
                await bot.send_message(message.chat.id, "Enter function to draw or go main menu")
    elif chat_status == Status.SETTINGS:
        logger.debug(message.text)
        match message.text:
            case 'Main menu':
                await go_main(message)
                return
            case 'On meme':
                try:
                    chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"meme": True}})
                except errors.PyMongoError:
                    await bot.send_message(message.chat.id, no_db_message)
            case 'Off meme':
                try:
                    chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"meme": False}})
                except errors.PyMongoError:
                    await bot.send_message(message.chat.id, no_db_message)
            case 'Set en language':
                try:
                    chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"lang": 'en'}})
                except errors.PyMongoError:
                    await bot.send_message(message.chat.id, no_db_message)
            case 'Set ru language':
                try:
                    chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"lang": 'ru'}})
                except errors.PyMongoError:
                    await bot.send_message(message.chat.id, no_db_message)
            case _:
                await message.reply(hmsg.echo())
                return
        await bot.send_message(message.chat.id, "New settings saved")
        await go_settings(message)


@dispatcher.errors_handler()
def error(update: types.Update, exception: TelegramAPIError):
    """Log Errors caused by Updates."""
    logger.error('Update %s\nCaused error %s', update, exception)


if __name__ == '__main__':
    init_pymongo_db()
    Graph.setup_plot_style()
    logger.info('Bot is started')
    dispatcher.middleware.setup(LoggingMiddleware(logger=logger))
    dispatcher.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dispatcher, skip_updates=True)
