"""
Database module
"""
import logging

from aiogram import types, Bot
from motor.motor_asyncio import AsyncIOMotorClient


from source.conf.config import Config
from source.extras.status import Status
from source.extras.translation import _, i18n
from source.keyboards.reply_keyboards import go_analyse_menu_markup, go_main_markup, go_graph_markup, \
    go_analyse_option, go_analyse_markup, go_settings_markup

no_db_message = "There were problems, the functionality is limited.\nYou can only use the bot with commands."


class MongoDatabase:

    """Mongo database"""
    def __init__(self, logger_, bot_):
        self.conf = Config()
        self.logger: logging.Logger = logger_
        self.bot: Bot = bot_
        self.client = AsyncIOMotorClient(
            f"mongodb://{self.conf.properties['DB_PARAMS']['ip']}:{self.conf.properties['DB_PARAMS']['port']}/",
            serverSelectionTimeoutMS=3000)
        self.db = None
        self.chat_status_table = None

    async def init(self):
        """Initialise connection to mongo database"""
        try:
            self.db = self.client[self.conf.properties["DB_PARAMS"]["database_name"]]
            self.chat_status_table = self.db["chat_status"]
            await self.chat_status_table.create_index("chat_id", unique=True)
            self.logger.debug(await self.client.server_info())
            self.logger.debug("Database connection installed")
        except Exception as exc:
            self.logger.warning(f"Unable to connect to the MongoDB server:\n{exc}")

    async def change_user_status(self, message: types.Message, status: Status) -> int:
        """Update user status in mongo database. It returns 1 if the connection is lost and 0 if all ok"""
        try:
            if (await self.chat_status_table.find_one({"chat_id": message.chat.id})) is None:
                await self.chat_status_table.insert_one({"chat_id": message.chat.id, "status": status.value,
                                                         "lang": message.from_user.language_code,
                                                         "meme": False})
            else:
                await self.chat_status_table.update_one({"chat_id": message.chat.id},
                                                        {"$set": {"status": status.value}})
            return 0
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
            return 1

    async def set_meme(self, message: types.Message, switcher: bool):
        """Turn on/off the meme button"""
        try:
            await self.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"meme": switcher}})
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
            return 1

    async def set_language(self, message: types.Message, language: str):
        """Set the language of the user"""
        try:
            await self.chat_status_table.update_one({"chat_id": message.chat.id}, {"$set": {"lang": language}})
            message.from_user.language_code = language
            await i18n.trigger("pre_process_message", (message, {}))  # Trigger i18n middleware to change the language
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
            return 1

    async def go_main(self, message: types.Message):
        """Change status of user and send main menu to user."""
        if await self.change_user_status(message, Status.MAIN):
            return
        try:
            meme_is_active = (await self.chat_status_table.find_one({"chat_id": message.chat.id}))['meme']
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
            return
        await self.bot.send_message(message.chat.id, _('Choose an action'),
                                    reply_markup=(await go_main_markup(meme_is_active)))

    async def go_settings(self, message: types.Message):
        """Change status of user and send settings menu to user."""
        if await self.change_user_status(message, Status.SETTINGS):
            return
        try:
            user_settings = await self.chat_status_table.find_one({"chat_id": message.chat.id})
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
            return
        await self.bot.send_message(message.chat.id,
                                    _("Your settings\nLanguage: {}\nMeme: {}")
                                    .format(user_settings['lang'], _('on') if user_settings['meme'] else _('off')))

        await self.bot.send_message(message.chat.id, _("Select the setting you want to apply."),
                                    reply_markup=(await go_settings_markup(user_settings)))

    async def go_graph(self, message: types.Message):
        """Change status of user and send draw graph menu to user."""
        if await self.change_user_status(message, Status.GRAPH):
            return
        await self.bot.send_message(message.chat.id, _("Enter a function you want to draw or go to the main menu"),
                                    reply_markup=(await go_graph_markup()))

    async def go_analyse(self, message: types.Message):
        """Change status of user to 'analyse' and send analyse menu"""
        if await self.change_user_status(message, Status.ANALYSE):
            return
        await self.bot.send_message(message.chat.id, _("Choose an option or enter your request or go to the main menu"),
                                    reply_markup=(await go_analyse_markup()))

    async def go_analyse_menu(self, message: types.Message):
        """Change status of user to 'analyze menu' and send options to analyze menu'"""
        if await self.change_user_status(message, Status.ANALYSE_MENU):
            return
        await self.bot.send_message(message.chat.id, _("Choose option to analyse or go back"),
                                    reply_markup=(await go_analyse_menu_markup()))

    async def go_analyse_option(self, message: types.Message, option: Status):
        """Change status of user to option and send 'go back' menu'"""
        if await self.change_user_status(message, option):
            return
        await self.bot.send_message(message.chat.id, _("Enter a function to analyse or go back"),
                                    reply_markup=(await go_analyse_option()))

    async def user_language(self, message: types.Message) -> str:
        """Return language of user"""
        try:
            return (await self.chat_status_table.find_one({"chat_id": message.chat.id}))['lang']
        except AttributeError:
            return "en"
        except TypeError:  # if user not in database
            return message.from_user.language_code
        except Exception as exc:
            await self.bot.send_message(message.chat.id, _(no_db_message))
            self.logger.warning(exc)
