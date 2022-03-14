"""
Main core module with bot and logger functionality
"""
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from handling_msg import Handler
from source.conf.config import Config
from source.core.database import MongoDatabase
from source.extras.custom_logger import setup_logging
from source.math.graph import Graph
from source.middleware.anti_flood_middleware import ThrottlingMiddleware
from source.middleware.localization_middleware import LanguageMiddleware


if __name__ == '__main__':
    # Enable logging
    logger = logging.getLogger(__name__)
    setup_logging(logger)

    # Set up a bot
    token: str = Config().properties["APP"]["TOKEN"]
    bot: Bot = Bot(token=token)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())

    # Init database
    mongo = MongoDatabase(logger, bot)

    # Set up translator
    dispatcher.middleware.setup(LanguageMiddleware("Bot", path=Path(__file__).parents[2] / "locales", mongo=mongo))

    # Init handler
    Handler(bot, mongo, logger, dispatcher)

    Graph.setup_plot_style()
    logger.info('Bot is started')
    dispatcher.middleware.setup(LoggingMiddleware(logger=logger))
    dispatcher.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dispatcher, skip_updates=True)
