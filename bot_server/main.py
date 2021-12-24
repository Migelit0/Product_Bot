# -*- coding: utf-8 -*-

import coloredlogs
import json
import logging
import os
import telebot
from app.bot import Bot
from app.shop_communication import DeliveryBot
from app.utilities import format_text
from dotenv import load_dotenv

if __name__ == '__main__':
    # создаем логгер
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG')

    # загружаем анекдоты
    with open('data/jokes.json', 'r', encoding='utf-8') as file:
        jokes = json.loads(file.read())

    # загружаем ответы бота
    with open('app/intents.json', 'r', encoding='utf-8') as file:
        intents = json.loads(file.read())

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
    http_pass = os.getenv('AUTH_PASSWORD')
    http_user = os.getenv('AUTH_USERNAME')
    server_ip = os.getenv('server_ip')
    server_port = os.getenv('server_port')

    # инициализация всех систем
    bot = telebot.TeleBot(TOKEN)
    logger.info('Connected to telegram')

    nlp_bot = Bot(jokes, './data/models_trained/', intents)
    logger.info('Created nlp bot')

    net_bot = DeliveryBot(db_name, db_user, db_pass, db_host, (http_user, http_pass), server_ip, server_port)
    logger.info('Created net bot')


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    bot.send_message(message.from_user.id,
                     'Привет! Поболтай со мной. Хоть я и не очень умный, но я готов учиться!\n'
                     'Мои ~~внутренности~~ исходники можно найти на '
                     'https://github.com/Migelit0/Product_Bot')


@bot.message_handler(content_types=['text'])
def answer_brilliant(message):
    """ Перехватываем все сообщения """
    text = format_text(message.text)
    answer, answer_type = nlp_bot.get_answer(text)
    logger.debug(f'User:{message.text}\tBot:{answer, answer_type}')
    if answer_type == 'M':
        bot.send_message(message.from_user.id, answer)
    elif answer_type == 'P':
        requested_categories = []  # запоминаем категории которые закалази для дальнейшего отчета
        declined_categories = []  # запоминаем запросы, по которым нет данных в бд

        for word in text.lower().split():
            with open('data/categories.json', 'r') as file:
                categories_data = json.loads(file.read())['categories']

            for category in categories_data:  # парсим все слова на предмет категории
                if word == category or word in categories_data[category]:  # word является категорией, надо заказать
                    is_ok = net_bot.request_by_category(category, net_bot.get_id_by_tg(message.from_user.id))

                    if not is_ok:
                        declined_categories.append(category)
                    else:
                        requested_categories.append(category)

        splitter = '\n*'
        if requested_categories and declined_categories:
            msg = f'Добавил в корзину продукты из категорий \n*{splitter.join(requested_categories)}'
            msg += f'\nНе найдены товары в категориях \n*{splitter.join(declined_categories)}'
        elif requested_categories:
            msg = f'Добавил в корзину продукты из категорий \n*{splitter.join(requested_categories)}'
        elif declined_categories:
            msg = f'Не найдены товары в категориях \n*{splitter.join(declined_categories)}'
        else:
            msg = 'Извините, я не нашел продуктов в вашем сообщении'

        bot.send_message(message.from_user.id, msg)

        if len(requested_categories) == 0:  # ищем конкретный товар
            msg = message.text.split()
            product_name = msg[1:]


@bot.message_handler(
    content_types=['sticker', 'document', 'audio', 'photo', 'video', 'video_note', 'voice', 'location', 'contact'])
def not_text_answer(message):
    bot.send_message(message.from_user.id, 'Буквами пиши але')


logger.info('Started telegram bot')

while True:
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as ex:
        logger.error('ERROR ' * 10 + str(ex))
