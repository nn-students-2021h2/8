"""
Main core module with bot and logger functionality
"""

import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

import handling_msg as hmsg
from source.conf.config import Config
from source.math.graph import Graph

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MAIN, GRAPH = range(2)

chats_status_dict = {}
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def go_main(update: Update):
    """Change status of user and send main menu to user."""
    chats_status_dict[update.message.chat_id] = MAIN
    reply_markup = ReplyKeyboardMarkup([['Draw graph']], resize_keyboard=True)
    update.message.reply_text('Choose action', reply_markup=reply_markup)


def go_graph(update: Update):
    """Change status of user and send draw graph menu to user."""
    chats_status_dict[update.message.chat_id] = GRAPH
    reply_markup = ReplyKeyboardMarkup([['Main menu']], resize_keyboard=True)
    update.message.reply_text("Enter function to draw or go to main menu", reply_markup=reply_markup)


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hello, {update.effective_user.first_name} {update.effective_user.last_name}!')
    go_main(update)


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')


def echo(update: Update, context: CallbackContext):
    """Check user status and directs his message to suitable function."""
    if chats_status_dict[update.message.chat_id] == MAIN:
        if update.message.text == 'Draw graph':
            go_graph(update)
        else:
            update.message.reply_text(hmsg.echo(update.message.text))
    elif chats_status_dict[update.message.chat_id] == GRAPH:
        if update.message.text == 'Main menu':
            go_main(update)
        else:
            hmsg.send_graph(update, context)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update %s\nCaused error %s', update, context.error)


def graph(update: Update, context: CallbackContext):
    """Draw graph, save it as image and send to the user."""
    if update.message.text == '/graph':
        go_graph(update)
    else:
        hmsg.send_graph(update, context)


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

    # On non-command i.e. message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

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
