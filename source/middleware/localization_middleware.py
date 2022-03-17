"""
Middleware for localization
"""
from typing import Tuple, Any, Optional

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


async def get_language(user: types.User, mongo):
    """
    Pull user's language code from database
    :param user: requested user
    :param mongo: database
    :return: language code (e.g. "en", "ru")
    """
    try:
        return await mongo.user_language(user)
    except Exception as exc:
        mongo.logger.warning(exc)
        return "en"


class LanguageMiddleware(I18nMiddleware):
    """Translation middleware"""

    def __init__(self, domain, path, mongo):
        super().__init__(domain, path=path)
        self.mongo = mongo

    # pylint: disable=no-self-use
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        """
        Request user's language code from database if it exists. If it doesn't exist, then returns default ("en")
        :param action: event name
        :param args: event args
        :return: language code
        """
        user = types.User.get_current()
        return await get_language(user, self.mongo) or "en"
