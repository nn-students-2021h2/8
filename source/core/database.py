"""
Database module
"""
from source.conf.config import Config
from pymongo import MongoClient, errors
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

from source.extras.status import Status
from source.extras.translation import _


no_db_message = "There were problems, the functionality is limited.\nYou can only use the bot with commands."


class MongoDatabase:
    """Mongo database"""
    def __init__(self, logger, bot):
        """Initialise connection to mongo database"""
        conf = Config()
        client = MongoClient(conf.properties["DB_PARAMS"]["ip"], conf.properties["DB_PARAMS"]["port"],
                             serverSelectionTimeoutMS=5000)
        try:
            logger.debug(client.server_info())
        except errors.PyMongoError:
            logger.critical("Unable to connect to the MongoDB server.")
        db = client[conf.properties["DB_PARAMS"]["database_name"]]
        self.chat_status_table = db["chat_status"]
        self.chat_status_table.create_index("chat_id", unique=True)
        self.bot = bot

    async def change_user_status(self, message: types.Message, status: Status) -> int:
        """Update user status in mongo database. It returns 1 if the connection is lost and 0 if all ok"""
        try:
            if self.chat_status_table.find_one({"chat_id": message.chat.id}) is None:
                self.chat_status_table.insert_one({"chat_id": message.chat.id, "status": status.value,
                                                                               "lang": message.from_user.language_code,
                                                                               "meme": False})
            else:
                self.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"status": status.value}})
            return 0
        except errors.PyMongoError:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            return 1

    async def go_main(self, message: types.Message):
        """Change status of user and send main menu to user."""
        if await self.change_user_status(message, Status.MAIN):
            return
        try:
            meme_is_active = self.chat_status_table.find_one({"chat_id": message.chat.id})['meme']
        except errors.PyMongoError:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            return
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Draw graph")
        reply_markup.add("Analyse function")
        reply_markup.add("Settings")
        reply_markup.add("Get help")
        if meme_is_active:
            reply_markup.add("Meme")
        await self.bot.send_message(message.chat.id, _('Choose action'), reply_markup=reply_markup)

    async def go_settings(self, message: types.Message):
        """Change status of user and send settings menu to user."""
        if await self.change_user_status(message, Status.SETTINGS):
            return
        try:
            user_settings = self.chat_status_table.find_one({"chat_id": message.chat.id})
        except errors.PyMongoError:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            return
        await self.bot.send_message(message.chat.id, f"Your settings\n"
                                                     f"Language: {user_settings['lang']}\n"
                                                     f"Meme: {'on' if user_settings['meme'] else 'off'}")
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        reply_markup.add(f"Set {'ru' if user_settings['lang'] == 'en' else 'en'} language")
        reply_markup.add(f"{'Off' if user_settings['meme'] else 'On'} meme")
        reply_markup.add("Main menu")
        await self.bot.send_message(message.chat.id, "Choose changes that you want.", reply_markup=reply_markup)

    async def go_graph(self, message: types.Message):
        """Change status of user and send draw graph menu to user."""
        if await self.change_user_status(message, Status.GRAPH):
            return
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Main menu")
        await self.bot.send_message(message.chat.id, _("Enter function you want to draw or go to the main menu"),
                                    reply_markup=reply_markup)

    async def go_analyse(self, message: types.Message):
        """Change status of user to 'analyse' and send analyse menu"""
        if await self.change_user_status(message, Status.ANALYSE):
            return
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Options")
        reply_markup.add("Get help")
        reply_markup.add("Main menu")
        await self.bot.send_message(message.chat.id, _("Choose option or enter command or go to main menu"),
                                    reply_markup=reply_markup)

    async def go_analyse_menu(self, message: types.Message):
        """Change status of user to 'analyze menu' and send options to analyze menu'"""
        if await self.change_user_status(message, Status.ANALYSE_MENU):
            return
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add('Derivative', 'Domain', 'Range',
                                                                     'Stationary points', 'Periodicity',
                                                                     'Continuity', 'Convexity', 'Concavity',
                                                                     'Horizontal asymptotes', 'Vertical asymptotes',
                                                                     'Asymptotes', 'Evenness', 'Oddness',
                                                                     'Axes intersection', 'Slant asymptotes',
                                                                     'Maximum', 'Minimum', 'Zeros',
                                                                     'Main menu', 'Back')
        await self.bot.send_message(message.chat.id, _("Choose option to analyse or go back"),
                                    reply_markup=reply_markup)

    async def go_analyse_option(self, message: types.Message, option: Status):
        """Change status of user to option and send 'go back' menu'"""
        if await self.change_user_status(message, option):
            return
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Back")
        reply_markup.add("Main menu")
        await self.bot.send_message(message.chat.id, _("Enter function to analyse or go back"),
                                    reply_markup=reply_markup)

    async def user_language(self, message: types.Message) -> str:
        """Return language of user"""
        try:
            return self.chat_status_table.find_one({"chat_id": message.chat.id})['lang']
        except errors.PyMongoError:
            await self.bot.send_message(message.chat.id, _(no_db_message))
        except TypeError:  # if user not in database
            return message.from_user.language_code
