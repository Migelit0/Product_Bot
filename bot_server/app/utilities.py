import re

import nltk
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
