# -*- coding: utf-8 -*-

import nltk
import re
from nltk import pos_tag
from nltk.stem import wordnet


def get_messages_by_tag(data: list, tag: str):
    for elem in data:
        if elem['tag'] == tag:
            return elem['responses']


def format_text(message: str):
    formated = re.sub(r'[^ еЁА-яa-z]', '',
                      str(message).lower())  # Преобразуем в нижний регистр. Удаоляем ненужные символы
    tokens = nltk.word_tokenize(formated)
    lema = wordnet.WordNetLemmatizer()
    tags_list = pos_tag(tokens, tagset=None)
    lema_words = []

    for token, pos_token in tags_list:
        if pos_token.startswith('V'):
            pos_val = 'v'
        elif pos_token.startswith('J'):
            pos_val = 'a'
        elif pos_token.startswith('R'):
            pos_val = 'r'
        else:
            pos_val = 'n'

        lema_token = lema.lemmatize(token, pos_val)
        lema_words.append(lema_token)

    return ' '.join(lema_words)


def generate_report_text(requested_products, declined_categories, maybe_products):
    """ Генерируем текст, оповещающий пользователя о купленных товарах """
    msg = ''
    if requested_products:
        msg += 'Добавил в корзину следующие товары:\n'
        for elem in requested_products:
            msg += f'*{elem[1]["name"]} ({elem[0]})\n'

    if declined_categories:
        msg += 'Не найдены товары в категориях:\n'
        for elem in declined_categories:
            msg += f'*{elem}'

    if maybe_products and not requested_products and not declined_categories:
        msg += 'Название продукта имеет несколько сходств.\nНапишите "Закажи [полное название]"\n'
        for elem in maybe_products:
            msg += f'*{elem["name"]}\n'

    if not msg:  # Ничего не засунули
        msg = 'Извините, я подумал, что вы хотите заказать товары, но видимо ошибся.\n' \
              'Однако, если вы все же хотели заказать, то напишите мне \n"Закажи [название товара или категории]"'

    return msg


def generate_bag_text(bag: dict):
    """ Генерируем текстовое представление корзины """
    products = {}

    if bag:  # на всякий слцчай
        msg = 'Вот что я нашел в вашей корзине:\n'
        for elem in bag:  # переформатируем все чтобы удобно было генерить
            product_id = elem['id']
            if product_id in products:
                products[product_id]['number'] += 1
            else:
                products[product_id] = elem
                products[product_id]['number'] = 1

        print(products)

        for product in products.values():
            if product['name']:
                msg += f"* {product['number']}х {product['name']}\n"
    else:
        msg = 'Ваша корзина пуста'

    return msg


def generate_recommendation_text(products: dict):
    """ Генерит текст о топе продуктов для пользователя """

    msg = ''

    if products:
        for category in products:
            if products[category]:
                msg += f'В категории {category} подобраны следующие товары для вас:\n'
                for elem in products[category]:
                    if elem and elem['id']:
                        msg += f'* {elem["name"]}\n'

                msg += '\n'

    if not msg:
        msg = 'В данных категориях не найдены товары'

    return msg
