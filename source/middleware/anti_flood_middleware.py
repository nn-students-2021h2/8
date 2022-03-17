"""
Anti-flood middleware preventing spamming
"""
import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from source.extras.translation import _


def rate_limit(limit: float, key=None):
    """
    Decorator for configuring rate limit and key in different functions
    :param limit: number of seconds to wait before unlocking
    :param key: name of handler
    :returns decorated function
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Anti-flood middlewares
    :param limit: number of seconds to wait before unlocking
    :param key_prefix: name of middleware
    """

    def __init__(self, limit=2, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        super().__init__()

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        await self.on_process_message(callback_query.message, data)

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message
        :param message: received message from user
        :param data: additional data
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

            # Cancel current handler
            raise CancelHandler() from t

    @staticmethod
    async def message_throttled(message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed and notify about unlocking only on last exceed
        :param message: throttled message
        :param throttled: information about throttled message and user
        """
        # Calculate how many times is left till the block ends
        delta = throttled.rate - throttled.delta

        # Prevent flooding
        # User can send only 3 requests before locking (bot will not answer further requests until unlocking)
        if throttled.exceeded_count <= 3:
            await message.reply(
                _("Flood is not allowed! You should wait {} seconds to repeat this action.").format(throttled.rate))

        # Sleep.
        await asyncio.sleep(delta)
