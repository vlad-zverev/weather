import json
import logging
from os import getenv
from traceback import format_exc

from pyowm.commons.exceptions import PyOWMError
from pyowm.owm import OWM
from pyowm.utils import config
from pyowm.weatherapi25.weather import Weather
from pyowm.weatherapi25.weather_manager import WeatherManager
from telebot import TeleBot
from telebot.types import Message


class Bot:
    """Telegram Bot, that handles requests for actual weather in city."""

    def __init__(self):
        self.bot = TeleBot(getenv('TELEGRAM_TOKEN'), parse_mode=None)
        self._weather_manager = self._initialize_weather_manager()
        self._initialize_handlers()
        with open('config.json', 'r') as response_map:
            self._response_map = json.loads(response_map.read())
        logging.info('Bot initialized')

    def start(self) -> None:
        """Start polling server."""
        logging.info('Bot start polling...')
        self.bot.infinity_polling(none_stop=True)

    @staticmethod
    def _initialize_weather_manager() -> WeatherManager:
        owm = OWM(api_key=getenv('WEATHER_API_KEY'))
        weather_manager: WeatherManager = owm.weather_manager()
        config.get_default_config()['language'] = 'ru'
        return weather_manager

    def _initialize_handlers(self) -> None:
        @self.bot.message_handler(commands=['start'])
        def handle_start_help(message: Message) -> None:
            self.bot.reply_to(message, 'Укажите город')

        @self.bot.message_handler(content_types=['text'])
        def handle_weather(message: Message) -> None:
            logging.info(f'Received message: {message.text} in chat: {message.chat}')
            try:
                weather = self._weather_manager.weather_at_place(message.text).weather
            except PyOWMError as error:
                self._send_response(message, f'Ошибочка: {error}, {format_exc()}')
                return
            temperature = weather.temperature(unit='celsius').get('temp')
            response = self._generate_response(message, temperature, weather)
            self._send_response(message, response)

    def _send_response(self, message: Message, text: str) -> None:
        logging.info('Response: %s', text)
        self.bot.send_message(message.chat.id, text)

    def _generate_response(self, message: Message, temperature: float, weather: Weather) -> str:
        response = (
            f'В городе {message.text} сейчас {weather.detailed_status}\n'
            + f'Температура примерно {temperature} °C\n\n'
        )
        for threshold, advise in self._response_map.items():
            if temperature < float(threshold):
                response += advise
                break
        return response
