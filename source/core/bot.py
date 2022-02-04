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
    """Enum for define statuses of chat"""
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
"""Dictionary that returns the Status of user by chat id"""


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
    """Change status of user to 'analyse' and send analyse menu"""
    chats_status_dict[update.message.chat_id] = Status.ANALYSE
    reply_markup = ReplyKeyboardMarkup([['Options'], ['Get help'], ['Main menu']], resize_keyboard=True)
    update.message.reply_text("Choose option or enter command or go to main menu", reply_markup=reply_markup)


def go_analyse_menu(update: Update):
    """Change status of user to 'analyze menu' and send options to analyze menu'"""
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
    """Change status of user to option and send 'go back' menu'"""
    chats_status_dict[update.message.chat_id] = option
    reply_markup = ReplyKeyboardMarkup([['Back'], ['Main menu']], resize_keyboard=True)
    update.message.reply_text("Enter function to analyse or go back", reply_markup=reply_markup)


status_dict = {
    'Derivative': Status.DERIVATIVE,
    'Domain': Status.DOMAIN,
    'Range': Status.RANGE,
    'Zeros': Status.ZEROS,
    'Axes intersection': Status.AXES_INTERSECTION,
    'Periodicity': Status.PERIODICITY,
    'Convexity': Status.CONVEXITY,
    'Concavity': Status.CONCAVITY,
    'Continuity': Status.CONTINUITY,
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
status_dict.update({value: key.lower() for key, value in status_dict.items()})


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hello, {update.effective_user.first_name} {update.effective_user.last_name}!')
    go_main(update)


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Enter:\n/start to restart bot.\n/graph to draw graph.\n/analyse to go on to investigate '
                              'the function.')


def default_handler(update: Update, context: CallbackContext):
    """Checks user status and direct his message to suitable function."""
    chat_status = chats_status_dict[update.message.chat_id]
    if chat_status == Status.MAIN:
        match update.message.text:
            case 'Draw graph':
                go_graph(update)
            case 'Analyse function':
                go_analyse(update)
            case 'Get help':
                chat_help(update, context)
            case _:
                update.message.reply_text(hmsg.echo(update.message.text))
    elif chat_status == Status.ANALYSE:
        match update.message.text:
            case 'Main menu':
                go_main(update)
            case 'Options':
                go_analyse_menu(update)
            case 'Get help':
                update.message.reply_text('No')
            case _:
                update.message.reply_text(hmsg.echo(update.message.text))
    elif chat_status == Status.ANALYSE_MENU:
        match update.message.text:
            case 'Back':
                go_analyse(update)
            case 'Main menu':
                go_main(update)
            case _:
                go_analyse_option(update, status_dict[update.message.text])
    elif Status.DERIVATIVE <= chat_status <= Status.STATIONARY_POINTS:
        match update.message.text:
            case 'Back':
                go_analyse_menu(update)
            case 'Main menu':
                go_main(update)
            case _:
                update.message.text = f'{status_dict[chat_status]} {update.message.text.lower()}'
                hmsg.send_analyse(update, context)
                update.message.reply_text("Enter function to explore or go back")
    elif chat_status == Status.GRAPH:
        match update.message.text:
            case 'Main menu':
                go_main(update)
            case _:
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
