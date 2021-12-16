import json
import os

import telebot
from dotenv import load_dotenv

from app.bot import Bot
from app.shop_communication import DeliveryBot
from app.utils import format_text


if __name__ == '__main__':
    # читаем данные из .env
    load_dotenv()
    TOKEN = os.getenv('API_KEY')
    db_name = os.getenv('db_name')
    db_host = os.getenv('db_host')
    db_user = os.getenv('db_user')
    db_type = os.getenv('db_type')
    db_port = os.getenv('db_port')
    db_pass = os.getenv('db_pass')
    token_password = os.getenv('token_password')
    http_pass = os.getenv('auth_password')
    http_user = os.getenv('auth_username')
    server_ip = os.getenv('server_ip')
    server_port = os.getenv('server_port')

    # инициализация всех систем
    bot = telebot.TeleBot(TOKEN)
    nlp_bot = Bot()
    net_bot = DeliveryBot(db_name, db_user, db_pass, db_host, (http_user, http_pass), server_ip, server_port)



@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    bot.send_message(message.from_user.id, 'Привет! Поболтай со мной. Хоть я и не очень умный, но я готов учиться!')


@bot.message_handler(func=lambda _: True)
def answer_brilliant(message):
    """ Перехватываем все сообщения """
    text = format_text(message.text)
    answer, type = nlp_bot.get_answer(text)
    if type == 'M':
        bot.send_message(message.from_user.id, answer)
    elif type == 'B':
        for word in text:
            with open('data/categories.json', 'r') as file:
                categories_data = json.loads(file.read())

            for category in categories_data:
                if word == category or word in categories_data[category]:   # word является категорией, надо заказать
                    net_bot.request_by_category(word, net_bot.get_id_by_tg(message.from_user.id))
