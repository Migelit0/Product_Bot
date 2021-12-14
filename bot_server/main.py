import os

import telebot
from dotenv import load_dotenv
from app.bot import Bot

from nlp.app import *

load_dotenv()
TOKEN = os.getenv('API_KEY')
bot = telebot.TeleBot(TOKEN)
nlp_bot = Bot()


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    bot.send_message(message.from_user.id, 'Привет! Поболтай со мной. Хоть я и не очень умный, но я готов учиться!')


@bot.message_handler(func=lambda _: True)
def answer_brilliant(message):
    """ Перехватываем все сообщения """
    answer, type = nlp_bot.get_answer(message.text)


if __name__ == '__main__':

    finder = NeiborFinder()  # создаем объект для поиска ответа
    finder.fit(matrix, raw.reply)
    pipe = make_pipeline(vectorizer, svd, finder)  # объект для обращения к предсказателю

    print('Bot started')

    bot.polling(none_stop=True, interval=0)