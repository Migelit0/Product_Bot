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

    if not msg: # Ничего не засунули
        msg = 'Извините, я подумал, что вы хотите заказать товары, но видимо ошибся.\n' \
              'Однако, если вы все же хотели заказать, то напишите мне \n"Закажи [название товара или категории]"'

    return msg
