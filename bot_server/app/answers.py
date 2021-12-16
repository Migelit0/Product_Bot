# -*- coding: utf-8 -*-

import re

import nltk
from nltk import pos_tag
from nltk.stem import wordnet


def get_response_type(response: str):
    """ Возращает тип запроса (купить, просто сообщение, из списка) """
    pass


def answer_from_file(filename: str):
    """ Возвращает ответ из жсон файла (решение в лоб) """
    pass


def answer_from_neural(model, response: str):
    """ Возращает ответ, сгенеренный нейронкой gpt-2 (или другой) """
    pass


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


if __name__ == '__main__':
    print(format_text('привет я твой друг! будем дРужить?'))