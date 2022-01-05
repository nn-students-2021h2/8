"""
Main core module with bot and logger functionality
"""

import logging

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

import handling_msg as hmsg

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
    logger.warning('Update %s caused error %s', update, context.error)


def graph(update: Update, context: CallbackContext):
    """Draw graph, save it as image and send to the user."""
    hmsg.send_graph(update, context)


def main():
    """
    Launch bot and
    """

    token = ''
    try:
        with open('source/conf/token.txt', encoding='utf-8') as token_file:
            token = token_file.readline()
    except IOError:
        logger.error('File token.txt is not found. Shutting down...')
        return

    updater = Updater(token, use_context=True)

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
