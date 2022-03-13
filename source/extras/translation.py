"""
File with gettext alias
"""
from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware

i18n = I18nMiddleware("Bot", Path(__file__).parents[2] / "locales")
_ = i18n.gettext
__ = i18n.gettext
