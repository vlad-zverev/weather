import logging
from os import getenv

from bot import Bot

logging.basicConfig(level=getenv('LOG_LEVEL'), format='%(asctime)s %(levelname)s (%(levelno)s) %(message)s')

bot = Bot()
if __name__ == '__main__':
    bot.start()
