# -*- coding: utf-8 -*-

import json
from random import choice

from neuralintents import GenericAssistant

from utils import *


class Bot:
    """
    Класс объединяет в себе все нейронки и функции для ответов
    Формат возращающихся значний - (сообщение, тип)
    Из типов:
    M - сообщение готовое
    P - запрос на заказ определеноого продукта  (не возращает обратно сообщение, ибо главный код имеет его уже)
    B - запрос на заказ корзины
    """

    def __init__(self, name='Григорий'):
        self.name = name
        # self.small_model = small_model  # легкая модель на сонове тщательно написанных ответов ранее
        # self.big_model = big_model  # модель на основе gpt-2, используется, если ответы ранее не были найдены

        mappings = {'greeting': self.function_for_greetings, 'empty': self.big_handler, 'buy': self.buy_one_thing,
                    'bag': self.buy_all_bag}
        # создаем модель, объявляем обработчики для каждого типа сообщений
        self.small_model = GenericAssistant('intents.json', intent_methods=mappings, model_name="small_model")
        # тренируем модель (ибо я хз как загружать уже созданную, а дедлайн просраьт не хочется)
        self.small_model.train_model()
        # self.small_model.save_model()

        self.message = ''   # буфер для возвращаегося значения

        with open('intents.json', 'r') as file:
            self.answers = json.loads(file.read())

    def get_answer(self, response: str):
        """ Суем сообщение в обработчик малой модели """
        self.small_model.request(response)
        return self.message

    def get_response_type(self, response: str):
        """ Возращает тип запроса (купить, просто сообщение, из списка) """

    def function_for_greetings(self):
        """ возращает сообщение чтобы поздороваться """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'greeting')), 'M'

    def buy_one_thing(self):
        """ Возращает пустое сообщение, чтобы основной код сделал заказ на продукт """
        self.message = None, 'P'

    def buy_all_bag(self):
        """ Возращает пустое сообщение, чтобы основной код сделал заказ на корзину """
        self.message = None, 'B'

    def big_handler(self):
        """ Здесь полномочия малой модели все, заапускаем тяжелую аретллерию """
        # TODO: ответ большей модели
        self.message = 'Big Model Message', 'M'


if __name__ == '__main__':
    assistant = Bot()

    done = False

    while not done:
        message = input('Enter a message: ')
        if message == 'STOP':
            done = True
        else:
            print(assistant.get_answer(message))
