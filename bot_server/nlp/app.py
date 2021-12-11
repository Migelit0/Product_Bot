import re
import re
import warnings
import coloredlogs, logging

import pandas as pd
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import wordnet
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

warnings.filterwarnings('ignore')

import nltk


def format_text(message: str):
    formated = re.sub(r'[^ еЁА-яa-z]', '', str(message).lower())  # Преобразуем в нижний регистр. Удаоляем ненужные символы
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


def predict_1(response_raw: str):
    response = []

    for word in response_raw.split():
        if word in stop:
            continue
        else:
            response.append(word)
    b = ' '.join(response)

    response_lemma = format_text(b)  # нормализуем текст просто
    response_bow = cv.transform([response_lemma]).toarray()  # получаем набор слов

    cosine_value = 1 - pairwise_distances(df_bow, response_bow, metric='cosine')  # считаем косинусное сходство
    return df['Text Response'].loc[cosine_value.argmax()]  # возвращаем самое близкое значение к запросу


def predict_2(response_raw: str):
    response = []

    for word in response_raw.split():
        if word in stop:
            continue
        else:
            response.append(word)
    b = ' '.join(response)

    response_lemma = format_text(b)  # нормализуем текст просто
    response_tfidf = tfidf.transform([response_lemma]).toarray()


    cosine_value = 1 - pairwise_distances(df_tfidf, response_tfidf, metric='cosine')  # считаем косинусное сходство
    return df['Text Response'].loc[cosine_value.argmax()]  # возвращаем самое близкое значение к запросу



if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG')

    df = pd.read_csv('data/save2.csv', sep=';;')
    df.ffill(axis=0, inplace=True)

    df['lemmatized_text'] = df['Context'].apply(format_text)

    stop = stopwords.words('russian')  # стоп-слова на русском

    var = 2
    if var == 1:
        cv = CountVectorizer()
        X = cv.fit_transform(df['lemmatized_text']).toarray()

        features = cv.get_feature_names()
        df_bow = pd.DataFrame(X, columns=features)  # считаем bag of words


        print('I am ready to talk!')
        while True:
            print('BOT: ' + predict_1(input('USER: ')))
    elif var == 2:
        tfidf = TfidfVectorizer()
        x_tfidf = tfidf.fit_transform(df['lemmatized_text']).toarray()

        df_tfidf = pd.DataFrame(x_tfidf, columns=tfidf.get_feature_names())

        print('I am ready to talk!')
        while True:
            print('BOT: ' + predict_2(input('USER: ')))


