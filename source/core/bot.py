"""
Main core module with bot and logger functionality
"""

import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

import handling_msg as hmsg
from source.conf.config import Config
from source.math.graph import Graph

from enum import Enum
from functools import total_ordering

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@total_ordering
class Status(Enum):
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

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


chats_status_dict = {}


def go_main(update: Update):
    """Change status of user and send main menu to user."""
    chats_status_dict[update.message.chat_id] = Status.MAIN
    reply_markup = ReplyKeyboardMarkup([['Draw graph'], ['Analyse function'], ['Get help']], resize_keyboard=True)
    update.message.reply_text('Choose action', reply_markup=reply_markup)


def go_graph(update: Update):
    """Change status of user and send draw graph menu to user."""
    chats_status_dict[update.message.chat_id] = Status.GRAPH
    reply_markup = ReplyKeyboardMarkup([['Main menu']], resize_keyboard=True)
    update.message.reply_text("Enter function to draw or go to main menu", reply_markup=reply_markup)


def go_analyse(update: Update):
    chats_status_dict[update.message.chat_id] = Status.ANALYSE
    reply_markup = ReplyKeyboardMarkup([['Options'], ['Get help'], ['Main menu']], resize_keyboard=True)
    update.message.reply_text("Choose option or enter command or go to main menu", reply_markup=reply_markup)


def go_analyse_menu(update: Update):
    chats_status_dict[update.message.chat_id] = Status.ANALYSE_MENU
    reply_markup = ReplyKeyboardMarkup([['Derivative', 'Domain', 'Range'],
                                        ['Stationary points', 'Periodicity'],
                                        ['Continuity', 'Convexity', 'Concavity'],
                                        ['Horizontal asymptotes', 'Vertical asymptotes'],
                                        ['Asymptotes', 'Evenness', 'Oddness'],
                                        ['Axes intersection', 'Slant asymptotes'],
                                        ['Maximum', 'Minimum', 'Zeros'],
                                        ['Main menu', 'Back']], resize_keyboard=True)
    update.message.reply_text("Choose option to analyze or go back", reply_markup=reply_markup)


def go_analyse_option(update: Update, option: Status):
    chats_status_dict[update.message.chat_id] = option
    reply_markup = ReplyKeyboardMarkup([['Back'], ['Main menu']], resize_keyboard=True)
    update.message.reply_text("Enter function to analyse or go back", reply_markup=reply_markup)


def name_analyse_option(option: Status) -> str:
    match option:
        case Status.DERIVATIVE:
            return 'derivative'
        case Status.DOMAIN:
            return 'domain'
        case Status.RANGE:
            return 'range'
        case Status.ZEROS:
            return 'zeros'
        case Status.AXES_INTERSECTION:
            return 'axes intersection'
        case Status.PERIODICITY:
            return 'periodicity'
        case Status.CONVEXITY:
            return 'convexity'
        case Status.CONCAVITY:
            return 'concavity'
        case Status.CONTINUITY:
            return 'continuity'
        case Status.V_ASYMPTOTES:
            return 'vertical asymptotes'
        case Status.H_ASYMPTOTES:
            return 'horizontal asymptotes'
        case Status.S_ASYMPTOTES:
            return 'slant asymptotes'
        case Status.ASYMPTOTES:
            return 'asymptotes'
        case Status.EVENNESS:
            return 'evenness'
        case Status.ODDNESS:
            return 'oddness'
        case Status.MAXIMUM:
            return 'maximum'
        case Status.MINIMUM:
            return 'minimum'
        case Status.STATIONARY_POINTS:
            return 'stationary points'
        case _:
            print("incorrect entry")
            return ""


def status_analyze_option(name: str) -> Status:
    match name:
        case "Derivative":
            return Status.DERIVATIVE
        case "Domain":
            return Status.DOMAIN
        case "Range":
            return Status.RANGE
        case "Zeros":
            return Status.ZEROS
        case "Axes intersection":
            return Status.AXES_INTERSECTION
        case "Periodicity":
            return Status.PERIODICITY
        case "Convexity":
            return Status.CONVEXITY
        case "Concavity":
            return Status.CONCAVITY
        case "Continuity":
            return Status.CONTINUITY
        case "Vertical asymptotes":
            return Status.V_ASYMPTOTES
        case "Horizontal asymptotes":
            return Status.H_ASYMPTOTES
        case "Slant asymptotes":
            return Status.S_ASYMPTOTES
        case "Asymptotes":
            return Status.ASYMPTOTES
        case "Evenness":
            return Status.EVENNESS
        case "Oddness":
            return Status.ODDNESS
        case "Maximum":
            return Status.MAXIMUM
        case "Minimum":
            return Status.MINIMUM
        case "Stationary points":
            return Status.STATIONARY_POINTS
        case _:
            logger.warning("Incorrect analyze option")


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hello, {update.effective_user.first_name} {update.effective_user.last_name}!')
    go_main(update)


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Enter:\n/start to restart bot.\n/graph to draw graph.\n/analyse to go explore function.')


def default_handler(update: Update, context: CallbackContext):
    """Check user status and directs his message to suitable function."""
    chat_status = chats_status_dict[update.message.chat_id]
    if chat_status == Status.MAIN:
        if update.message.text == 'Draw graph':
            go_graph(update)
        elif update.message.text == 'Analyse function':
            go_analyse(update)
        elif update.message.text == 'Get help':
            chat_help(update, context)
        else:
            update.message.reply_text(hmsg.echo(update.message.text))
    elif chat_status == Status.ANALYSE:
        if update.message.text == 'Main menu':
            go_main(update)
        elif update.message.text == 'Options':
            go_analyse_menu(update)
        elif update.message.text == 'Get help':
            update.message.reply_text('No')
        else:
            update.message.reply_text(hmsg.echo(update.message.text))
    elif chat_status == Status.ANALYSE_MENU:
        if update.message.text == 'Back':
            go_analyse(update)
        elif update.message.text == 'Main menu':
            go_main(update)
        else:
            go_analyse_option(update, status_analyze_option(update.message.text))
    elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
        if update.message.text == 'Back':
            go_analyse_menu(update)
        elif update.message.text == 'Main menu':
            go_main(update)
        else:
            update.message.text = f'{name_analyse_option(chat_status)} {update.message.text.lower()}'
            hmsg.send_analyse(update, context)
            update.message.reply_text("Enter function to explore or go back")
    elif chat_status == Status.GRAPH:
        if update.message.text == 'Main menu':
            go_main(update)
        else:
            hmsg.send_graph(update, context)
            update.message.reply_text("Enter function to draw or go main menu")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update %s\nCaused error %s', update, context.error)


def graph(update: Update, context: CallbackContext):
    """Draw graph, save it as image and send to the user."""
    if update.message.text == '/graph':
        go_graph(update)
    else:
        hmsg.send_graph(update, context)


def analyse(update: Update, context: CallbackContext):
    """Calculate requested function and send result to the user in LaTeX format (or not LaTeX - check config file)"""
    if update.message.text == '/analyse':
        go_analyse(update)
    else:
        hmsg.send_analyse(update, context)


def main():
    """
    Set configuration and launch bot
    """

    conf = Config()
    token = conf.properties["APP"]["TOKEN"]

    updater = Updater(token, use_context=True)

    # Config plot style and save settings
    Graph.setup_plot_style()

    # On different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('graph', graph))
    updater.dispatcher.add_handler(CommandHandler('analyse', analyse))

    # On non-command i.e. message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, default_handler))

    # Log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Bot is started')
    main()
