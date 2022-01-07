"""
Main core module with bot and logger functionality
"""

import logging

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

import handling_msg as hmsg
from source.conf.config import Config
from source.math.graph import Graph

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(hmsg.echo(update.message.text))


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update %s\nCaused error %s', update, context.error)


def graph(update: Update, context: CallbackContext):
    """Draw graph, save it as image and send to the user."""
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
