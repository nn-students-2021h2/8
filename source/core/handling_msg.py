"""
In this module we process events related to bot (such as messages, requests)
"""
import logging
from io import BytesIO

import aiohttp
from aiogram import types, Bot
from aiogram.types import ParseMode
from aiogram.utils.exceptions import BadRequest, TelegramAPIError, PhotoDimensions
from pymongo import errors

import source.math.help_functions as hlp
from source.conf import Config
from source.core.database import MongoDatabase, no_db_message
from source.extras.status import Status
from source.extras.translation import _, graph_guide_texts, analysis_guide_texts
from source.extras.utilities import run_TeX, resize_image
from source.keyboards.inline_keyboards import chat_help_markup, reply_markup_graph, reply_markup_analysis
from source.math.calculus_parser import CalculusParser
from source.math.graph import Graph, DrawError
from source.math.graph_parser import GraphParser, ParseError
from source.math.math_function import MathError
from source.middleware.anti_flood_middleware import rate_limit
from source.middleware.localization_middleware import get_language


class Handler:
    """Handler of bot commands and messages"""
    bot: Bot = None
    mongo: MongoDatabase = None
    logger: logging.Logger = None
    status_dict: dict = None
    # We get "USE_LATEX" parameter from settings
    SETTINGS: Config = None
    REQUEST_LENGTH_LIMIT: int = 1000

    def __init__(self, bot_, mongo_, logger_, dispatcher):
        Handler.bot = bot_
        Handler.mongo = mongo_
        Handler.logger = logger_
        Handler.status_dict = {
            'Derivative': Status.DERIVATIVE,
            'Domain': Status.DOMAIN,
            'Range': Status.RANGE,
            'Zeros': Status.ZEROS,
            'Axes intersection': Status.AXES_INTERSECTION,
            'Periodicity': Status.PERIODICITY,
            'Convexity': Status.CONVEXITY,
            'Concavity': Status.CONCAVITY,
            'Monotonicity': Status.MONOTONICITY,
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
        Handler.status_dict.update({value: key.lower() for key, value in Handler.status_dict.items()})
        Handler.SETTINGS = Config()

        @dispatcher.message_handler(commands=["start"])
        @rate_limit(limit=1)
        async def start(message: types.Message):
            """Send a message when the command /start is issued."""
            user = message.from_user
            await Handler.bot.send_message(message.chat.id, _('Hello, {} {}!').format(user.first_name, user.last_name))
            await Handler.mongo.go_main(message)

        @dispatcher.message_handler(commands=["help"])
        @rate_limit(limit=1)
        async def chat_help(message: types.Message):
            """Send a message when the command /help is issued."""
            await Handler.bot.send_message(message.chat.id, _(hlp.main_help()), reply_markup=(await chat_help_markup()))

        @dispatcher.message_handler(commands=["graph"])
        @rate_limit(limit=2)
        async def graph(message: types.Message):
            """Draw graph, save it as image and send to the user."""
            if message.text == '/graph':
                await Handler.mongo.go_graph(message)
            else:
                await Handler.send_graph(message)

        @dispatcher.message_handler(commands=["analyse"])
        @rate_limit(limit=2)
        async def analyse(message: types.Message):
            """Calculate requested function and send result to the user in LaTeX format
            (or not LaTeX - check config file)"""
            if message.text == '/analyse':
                await Handler.mongo.go_analyse(message)
            else:
                await Handler.send_analyse(message)

        @rate_limit(limit=2)
        async def meme(message: types.Message):
            """Call meme-api and send random meme from Reddit to user"""
            await Handler.send_meme(message)

        @dispatcher.message_handler(content_types=["text"])
        @rate_limit(limit=2)
        async def default_handler(message: types.Message):
            """Checks user status and direct his message to suitable function."""
            try:
                chat_status = Status((await
                                      Handler.mongo.chat_status_table.find_one({"chat_id": message.chat.id}))['status'])
            except Exception as exc:
                await Handler.bot.send_message(message.chat.id, _(no_db_message))
                Handler.logger.warning(exc)
                return

            text = message.text
            if chat_status == Status.MAIN:
                if text == _('Draw graph'):
                    await Handler.mongo.go_graph(message)
                elif text == _('Analyse function'):
                    await Handler.mongo.go_analyse(message)
                elif text == _('Get help'):
                    await chat_help(message)
                elif text == _('Meme'):
                    await meme(message)
                    return
                elif text == _('Settings'):
                    await Handler.mongo.go_settings(message)
                else:
                    await message.reply(_('I didn\'t understand what you want'))
            elif chat_status == Status.ANALYSE:
                if text == _('Main menu'):
                    await Handler.mongo.go_main(message)
                elif text == _('Options'):
                    await Handler.mongo.go_analyse_menu(message)
                elif text == _('Examples'):
                    await Handler.bot.send_message(message.chat.id, _("Choose analysis example"),
                                                   reply_markup=(await reply_markup_analysis(True)))
                else:
                    await Handler.send_analyse(message)
            elif chat_status == Status.ANALYSE_MENU:
                if text == _('Back'):
                    await Handler.mongo.go_analyse(message)
                elif text == _('Main menu'):
                    await Handler.mongo.go_main(message)
                else:
                    try:
                        status_dict_translated = {_(k): v for k, v in Handler.status_dict.items()}
                        await Handler.mongo.go_analyse_option(message, status_dict_translated[message.text])
                    except KeyError:
                        await Handler.send_analyse(message)
            elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
                if text == _('Back'):
                    await Handler.mongo.go_analyse_menu(message)
                elif text == _('Main menu'):
                    await Handler.mongo.go_main(message)
                else:
                    message.text = f'{Handler.status_dict[chat_status]} {message.text.lower()}'
                    await Handler.send_analyse(message)
                    await Handler.bot.send_message(message.chat.id, _("Enter a function to explore or go back"))
            elif chat_status == Status.GRAPH:
                if text == _('Main menu'):
                    await Handler.mongo.go_main(message)
                elif text == _('Examples'):
                    await Handler.bot.send_message(message.chat.id, _("Choose graph example"),
                                                   reply_markup=(await reply_markup_graph(True)))
                else:
                    await Handler.send_graph(message)
                    await Handler.bot.send_message(message.chat.id,
                                                   _("Enter a function you want to draw or go to the main menu"),
                                                   disable_notification=True)
            elif chat_status == Status.SETTINGS:
                Handler.logger.debug(message.text)
                try:
                    if text == _('Main menu'):
                        await Handler.mongo.go_main(message)
                        return
                    if text in [on := _('On meme button'), _('Off meme button')]:
                        await Handler.mongo.set_meme(message, text == on)
                    elif text in [_('Set en language'), _('Set ru language')]:
                        language = text.split()[1]
                        await Handler.mongo.set_language(message, language)
                    else:
                        await message.reply(_('I didn\'t understand what you want'))
                        return
                except errors.PyMongoError:
                    await Handler.bot.send_message(message.chat.id, _(no_db_message))
                await Handler.bot.send_message(message.chat.id, _("Settings saved"))
                await Handler.mongo.go_settings(message)

        @dispatcher.errors_handler()
        def error(update: types.Update, exception: TelegramAPIError):
            """Log Errors caused by Updates."""
            Handler.logger.error('Update %s\nCaused error %s', update, exception)

        @dispatcher.callback_query_handler(lambda c: c.data == 'graph_examples')
        async def graph_examples(callback_query: types.CallbackQuery):
            await Handler.bot.send_message(callback_query.from_user.id, _("Choose graph examples"),
                                           reply_markup=(await reply_markup_graph(False)))
            await Handler.bot.answer_callback_query(callback_query.id)

        @dispatcher.callback_query_handler(lambda c: c.data == 'analysis_examples')
        async def analysis_examples(callback_query: types.CallbackQuery):
            await Handler.bot.send_message(callback_query.from_user.id, _("Choose analysis examples"),
                                           reply_markup=(await reply_markup_analysis(False)))
            await Handler.bot.answer_callback_query(callback_query.id)

        @dispatcher.callback_query_handler(lambda c: c.data == 'graph_guide')
        async def graph_guide(callback_query: types.CallbackQuery):
            await Handler.bot.answer_callback_query(callback_query.id)
            for part in graph_guide_texts:
                await Handler.bot.send_message(callback_query.from_user.id, _(part), parse_mode=ParseMode.MARKDOWN)

        @dispatcher.callback_query_handler(lambda c: c.data == 'analysis_guide')
        async def analysis_guide(callback_query: types.CallbackQuery):
            await Handler.bot.answer_callback_query(callback_query.id)
            for part in analysis_guide_texts:
                await Handler.bot.send_message(callback_query.from_user.id, _(part), parse_mode=ParseMode.MARKDOWN)

        @dispatcher.callback_query_handler(lambda c: c.data and c.data.startswith('example_graph_'))
        async def example_graph(callback_query: types.CallbackQuery):
            await Handler.bot.answer_callback_query(callback_query.id, text=_('Task in work...'))
            expr = callback_query.message.reply_markup.inline_keyboard[int(callback_query.data[-1])][0].text
            message = callback_query.message
            if expr[0] == '/':
                expr = expr[len('/graph') + 1:]
            message.text = expr
            await Handler.send_graph(message)

        @dispatcher.callback_query_handler(lambda c: c.data and c.data.startswith('example_analysis_'))
        async def example_analysis(callback_query: types.CallbackQuery):
            await Handler.bot.answer_callback_query(callback_query.id, text=_('Task in work...'))
            expr = callback_query.message.reply_markup.inline_keyboard[int(callback_query.data[-1])][0].text
            message = callback_query.message
            if expr[0] == '/':
                expr = expr[len('/analyse') + 1:]
            message.text = expr
            await Handler.send_analyse(message)

    @staticmethod
    async def send_graph(message: types.Message):
        """User requested to draw a plot"""
        if message.get_command():
            expr = message.get_args().lower()
        else:
            expr = message.text.lower()
        chat_id = message.chat.id

        # Check if expression is not enormous
        if len(expr) > Handler.REQUEST_LENGTH_LIMIT:
            await Handler.bot.send_message(chat_id, _("The request is too long. "
                                                      "Sorry, you are limited to {} characters")
                                           .format(Handler.REQUEST_LENGTH_LIMIT))
            return

        user_language = await get_language(message.from_user, Handler.mongo)

        Handler.logger.info("User [chat_id=%s] requested to draw a graph. User's input: `%s`", chat_id, expr)

        parser = GraphParser()

        try:
            if not await parser.parse(expr, user_language):
                await Handler.bot.send_message(chat_id, _("Function execution time limit exceeded! "
                                                          "Sorry, it is a very hard problem to solve."))
                return

            graph = Graph()
            image = await graph.draw(parser, user_language)

        except ParseError as err:
            await message.reply(str(err))
            Handler.logger.info("ParseError exception raised on user's [chat_id=%s] input: `%s`\nException message: %s",
                                chat_id, expr, err)
            return
        except DrawError as err:
            await message.reply(str(err))
            Handler.logger.info("DrawError exception raised on user's [chat_id=%s] input: `%s`\nException message: %s",
                                chat_id, expr, err)
            return

        output_message = _("Here a graph of requested functions")
        await Handler.bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=output_message + '\n' + "\n".join(parser.warnings)
        )
        image.close()

        parser.clear_warnings()

    @staticmethod
    async def send_analyse(message: types.Message):
        """User requested some function analysis"""
        if message.get_command():
            expr = message.get_args().lower()
        else:
            expr = message.text.lower()
        chat_id = message.chat.id
        user_language = await get_language(message.from_user, Handler.mongo)

        Handler.logger.info("User [chat_id=%s] requested an analysis. User's input: `%s`", chat_id, expr)

        parser = CalculusParser()

        try:
            # Parse the request and check if any pattern was found
            # If parser can't understand what the user means, it returns False
            is_pattern_found = await parser.parse(expr, user_language)
            if not is_pattern_found:
                await message.reply(_("Couldn't find a suitable template. Check the input."))
                Handler.logger.info("Bot doesn't find any pattern for user's [id=%s] input: `%s`", chat_id, expr)
                return

            result = await parser.process_query(user_language)

            # If USE_LATEX set in True, then send picture to the user. Else, send basic text
            if Handler.SETTINGS.properties["APP"]["USE_LATEX"]:
                latex = parser.make_latex(result)
                with BytesIO() as latex_picture, BytesIO() as resized_image:
                    await run_TeX(latex, latex_picture)
                    await resize_image(latex_picture, resized_image)

                    # If we can't send photo due to Telegram limitations, then send image as file instead
                    try:
                        await Handler.bot.send_photo(
                            chat_id=chat_id,
                            photo=resized_image,
                            caption="\n".join(parser.warnings)
                        )
                    except (BadRequest, PhotoDimensions):
                        parser.push_warning(_("Photo size is too large, therefore I send you a file."))
                        await Handler.bot.send_document(
                            chat_id=chat_id,
                            document=resized_image,
                            caption="\n".join(parser.warnings)
                        )
            else:
                await Handler.bot.send_message(
                    chat_id=chat_id,
                    text=str(result)
                )
            parser.clear_warnings()
        except TimeoutError as err:
            await message.reply(str(err))
            Handler.logger.info("TimeoutError exception raised on user's [chat_id=%s] input: `%s`\nException message: "
                                "%s", chat_id, expr, err)
        except ParseError as err:
            await message.reply(_(str(err)))
            Handler.logger.info("ParseError exception raised on user's [chat_id=%s] input: `%s`\nException message: %s",
                                chat_id, expr, err)
        except MathError as err:
            await message.reply(_(str(err)))
            Handler.logger.info("MathError exception raised on user's [chat_id=%s] input: `%s`\nException message: %s",
                                chat_id, expr, err)
        except RecursionError as err:
            await message.reply(_("Incorrect input. Please check your function."))
            Handler.logger.warning(
                "RecursionError exception raised on user's [chat_id=%s] input: `%s`\nException message: %s", chat_id,
                expr, err)
        except (ValueError, TypeError, NotImplementedError, AttributeError) as err:
            await message.reply(
                _("Sorry, can't solve the problem or the input is invalid. Please check your function."))
            Handler.logger.warning("ValueError or NotImplementedError exception raised on "
                                   "user's [chat_id=%s] input: `%s`\nException message: %s", chat_id, expr, err)

    @staticmethod
    async def send_meme(message: types.Message):
        """User requested some meme"""
        chat_id = message.chat.id
        Handler.logger.info("User [id=%s] requested a meme", chat_id)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.herokuapp.com/gimme/") as data:
                response = await data.json()
                url = response["url"]
                post_link = response["postLink"]
            async with session.head(url) as data:
                headers = data.headers

        try:
            if headers["Content-Type"] == "image/gif":
                await Handler.bot.send_animation(
                    chat_id=chat_id,
                    animation=url,
                    caption=post_link
                )
            else:
                await Handler.bot.send_photo(
                    chat_id=chat_id,
                    photo=url,
                    caption=post_link
                )
        except BadRequest as err:
            Handler.logger.warning("User [id=%s] catches a BadRequest getting a meme: %s", chat_id, err)
            await Handler.bot.send_message(
                chat_id=chat_id,
                text=_("Sorry, something went wrong. Please try again later.")
            )
