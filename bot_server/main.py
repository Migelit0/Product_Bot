# -*- coding: utf-8 -*-

import coloredlogs
import json
import logging
import os
import telebot
from app.bot import Bot
from app.shop_communication import DeliveryBot
from app.utilities import format_text, generate_bag_text, generate_report_text, generate_recommendation_text
from dotenv import load_dotenv

if __name__ == '__main__':
    debug = True

    # создаем логгер
    logger = logging.getLogger(__name__)
    if debug:
        coloredlogs.install(level='DEBUG')
    else:
        coloredlogs.install(level='INFO')

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
    """ Создаем пользователя и высвечиваем приветственное сообщение"""
    message_text = """Привет! Поболтай со мной. Хоть я и не очень умный, но я готов учиться!\n
     Мои ~~внутренности~~ исходники можно найти на https://github.com/Migelit0/Product_Bot"""

    is_created = net_bot.create_user(message.from_user.id)
    if not is_created:
        message_text = """Привет! Возникла ошибка при привязке вашего аккаунта.\n
        Пожалуйста, обратитесь к админу (@Mige1ito) для решения этой проблемы."""
    else:
        if debug:
            net_bot.create_demo_profile(message.from_user.id)

    bot.send_message(message.from_user.id, message_text)


@bot.message_handler(content_types=['text'])
def answer_brilliant(message):
    """ Перехватываем все сообщения """
    text = format_text(message.text)
    answer, answer_type = nlp_bot.get_answer(text)
    logger.debug(f'User:{message.text}\tBot:{answer, answer_type}')
    if answer_type == 'M':
        msg = answer
    elif answer_type == 'P':  # Заказываем продукт
        requested_products = []  # запоминаем категории которые закалази для дальнейшего отчета
        declined_categories = []  # запоминаем запросы, по которым нет данных в бд
        maybe_products = []  # список продуктов, которые искал бот

        for word in text.lower().split():  # парсим все слова на предмет категории
            with open('data/categories.json', 'r') as file:
                categories_data = json.loads(file.read())['categories']

            for category in categories_data:
                if word == category or word in categories_data[category]:  # word является категорией, надо заказать
                    is_ok, product = net_bot.request_by_category(category, net_bot.get_id_by_tg(message.from_user.id))

                    if not is_ok:
                        declined_categories.append(category)
                    else:
                        requested_products.append((category, product))

        if len(requested_products) == 0:
            msg = message.text.split()
            product_name = ' '.join(msg[1:])
            products = net_bot.search_by_name(product_name)
            if products:  # хотфикс для Даника
                if len(products) == 1:  # подобный продукт один единственный
                    net_bot.request_by_id(products[0]['id'], message.from_user.id)
                    requested_products.append(
                        (products[0]['categories'].split(',')[0], products[0]))  # страшно, но работает (хотфикс)
                elif len(products) > 1:
                    maybe_products = products

        msg = generate_report_text(requested_products, declined_categories, maybe_products)
    elif answer_type == 'R':  # показывааем рекомендованные продукты (помогаем выбрать)
        all_products = {}

        for word in text.lower().split():  # парсим все слова на предмет категории
            with open('data/categories.json', 'r') as file:
                categories_data = json.loads(file.read())['categories']

            for category in categories_data:
                if word == category or word in categories_data[category]:  # word является категорией
                    is_ok, products = net_bot.get_recommendations(message.from_user.id, category)
                    if is_ok:
                        all_products[category] = products[:7]

        msg = generate_recommendation_text(all_products)
    elif answer_type == 'B':  # отправляем корзину
        bag = net_bot.get_user_bag(message.from_user.id)
        msg = generate_bag_text(bag)
    elif answer_type == 'C':  # очищаем корзину
        is_ok = net_bot.clear_user_bag(message.from_user.id)
        if is_ok:
            msg = 'Ваша корзина успешно очищена'
        else:
            msg = 'Что-то пошло не так.\n' \
                  'За расписанием тех работ следите на https://vk.com/projectorengym1 или пишите админу @Mige1ito'
    else:
        msg = 'Что-то пошло не так. \n' \
              'За расписанием тех работ следите на https://vk.com/projectorengym1 или пишите админу @Mige1ito'

    bot.send_message(message.from_user.id, msg)


@bot.message_handler(
    content_types=['sticker', 'document', 'audio', 'photo', 'video', 'video_note', 'voice', 'location', 'contact'])
def not_text_answer(message):
    bot.send_message(message.from_user.id, 'Буквами пиши але')


logger.info('Started telegram bot')

while True:
    try:  # сколько раз схема не подводила, поэтому не ругать
        bot.polling(none_stop=True, interval=1)
    except Exception as ex:
        logger.error('ERROR ' * 10 + str(ex))
