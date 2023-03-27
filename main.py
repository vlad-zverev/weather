import logging
from os import getenv
from sys import stdout

from bot import Bot

logging.basicConfig(
    level=getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s %(levelname)s (%(levelno)s) %(message)s',
    stream=stdout,
)

bot = Bot()
if __name__ == '__main__':
    bot.start()
