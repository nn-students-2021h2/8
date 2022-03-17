"""
Main core module with bot and logger functionality
"""
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from source.core.handling_msg import Handler
from source.conf.config import Config
from source.core.database import MongoDatabase
from source.extras.custom_logger import setup_logging
from source.math.graph import Graph
from source.middleware.anti_flood_middleware import ThrottlingMiddleware
from source.middleware.localization_middleware import LanguageMiddleware


async def init_db(logger_, bot_):
    """Async function to init database"""
    db = MongoDatabase(logger_, bot_)
    await db.init()
    return db


async def init_bot(dispatcher_, logger_, bot_):
    """Async function to call init_db and init translator and handler"""
    mongo_ = await init_db(logger, bot)
    await asyncio.sleep(5)
    # Set up translator
    dispatcher_.middleware.setup(LanguageMiddleware("Bot", path=Path(__file__).parents[2] / "locales", mongo=mongo_))

    # Init handler
    Handler(bot_, mongo_, logger_, dispatcher_)

    dispatcher_.middleware.setup(LoggingMiddleware(logger=logger))
    dispatcher_.middleware.setup(ThrottlingMiddleware())


async def log_start(*args):
    """Async function to log about starting bot"""
    logger.info('Bot is started')


async def log_stop(*args):
    """Async function to log about stopping bot"""
    logger.info('Bot is stopped')


if __name__ == '__main__':
    # Enable logging
    logger = logging.getLogger(__name__)
    setup_logging(logger)

    # Set up a bot
    token: str = Config().properties["APP"]["TOKEN"]
    bot: Bot = Bot(token=token)

    Graph.setup_plot_style()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dispatcher = Dispatcher(bot, storage=MemoryStorage(), loop=loop)
    dispatcher.loop.create_task(init_bot(dispatcher, logger, bot))
    executor.start_polling(dispatcher, skip_updates=True, on_startup=log_start, on_shutdown=log_stop)
