import os

import telebot
from dotenv import load_dotenv

from nlp.app import *

load_dotenv()
TOKEN = os.getenv('API_KEY')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    bot.send_message(message.from_user.id, 'Привет! Поболтай со мной. Хоть я и не очень умный, но я готов учиться!')


@bot.message_handler(func=lambda _: True)
def answer_brilliant(message):
    bot.send_message(message.from_user.id, pipe.predict([message.text.lower()]))


if __name__ == '__main__':
    matrix, raw, vectorizer, svd = init_objects('./nlp/data/good.tsv')  # делаем матрицу ответов и все необходимы объекты
    logging.info('Данные получены, матрицы сформированы.')

    finder = NeiborFinder()  # создаем объект для поиска ответа
    finder.fit(matrix, raw.reply)
    pipe = make_pipeline(vectorizer, svd, finder)  # объект для обращения к предсказателю

    print('Bot started')

    bot.polling(none_stop=True, interval=0)