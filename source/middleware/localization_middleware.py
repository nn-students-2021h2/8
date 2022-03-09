"""
Middleware for localization
"""
from typing import Tuple, Any, Optional

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


# TODO move function in database.py (sql.py)
async def get_language(user_id):
    """
    Pull user's language code from database
    :param user_id: id of requested user
    :return: language code (e.g. "en", "ru")
    """
    return "ru"


class LanguageMiddleware(I18nMiddleware):
    """Translation middleware"""

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        """
        Request user's language code from database if it exists. If it doesn't exist, then returns default ("en")
        :param action: event name
        :param args: event args
        :return: language code
        """
        user = types.User.get_current()
        return await get_language(user.id) or "en"
