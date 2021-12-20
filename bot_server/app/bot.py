# -*- coding: utf-8 -*-

import os
import random
from random import choice

from aitextgen import aitextgen
from app.utilities import get_messages_by_tag
from neuralintents import GenericAssistant


class Bot:
    """
    Класс объединяет в себе все нейронки и функции для ответов
    Формат возращающихся значний - (сообщение, тип)
    Из типов:
    M - сообщение готовое
    P - запрос на заказ определеноого продукта  (не возращает обратно сообщение, ибо главный код имеет его уже)
    B - запрос на заказ корзины
    """

    def __init__(self, jokes: dict, big_model_path: str, intents: dict, name='Григорий'):
        self.name = name
        self.jokes = jokes
        self.message = ('', '')  # буферы для значений
        self.response = ''
        self.start_temperature = 0.5
        self.max_temperature = 7.0

        self.answers = intents

        # self.small_model = small_model
        # self.big_model = big_model

        # создаем малую модель, объявляем обработчики для каждого типа сообщений
        mappings = {'greeting': self.function_for_greetings, 'empty': self.big_handler, 'buy': self.buy_one_thing,
                    'bag': self.buy_all_bag, 'joke': self.tell_joke, 'howreu': self.function_howareyou}
        # TODO: Подключить остальные группы ответов

        self.small_model = GenericAssistant('app/intents.json', intent_methods=mappings,
                                            model_name="small_model")  # легкая модель на сонове тщательно написанных ответов ранее
        # тренируем модель (ибо я хз как загружать уже созданную, а дедлайн просраьт не хочется)
        self.small_model.train_model()
        # self.small_model.save_model()

        files = os.listdir(big_model_path)
        files.remove('.gitkeep')
        folder_name = files[0]

        model_path = os.path.join("data", "models_trained", folder_name, "pytorch_model.bin")
        config_path = os.path.join("data", "models_trained", folder_name, "config.json")
        vocab_path = os.path.join("data", "models_trained", folder_name, "aitextgen-vocab.json")
        merges_path = os.path.join("data", "models_trained", folder_name, "aitextgen-merges.txt")

        self.big_model = aitextgen(model=model_path,
                                   config=config_path,
                                   vocab_file=vocab_path,
                                   merges_file=merges_path,
                                   to_gpu=False)  # модель на основе gpt-2, используется, если ответы ранее не были найдены

    def get_answer(self, response: str):
        """ Суем сообщение в обработчик малой модели """
        self.response = response
        self.small_model.request(response)
        return self.message

    def get_response_type(self):
        """ Возращает тип запроса (купить, просто сообщение, из списка) """

    def function_for_greetings(self):
        """ возращает сообщение чтобы поздороваться """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'greeting')), 'M'

    def function_howareyou(self):
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'howreu')), 'M'

    def buy_one_thing(self):
        """ Возращает пустое сообщение, чтобы основной код сделал заказ на продукт """
        self.message = None, 'P'

    def buy_all_bag(self):
        """ Возращает пустое сообщение, чтобы основной код сделал заказ на корзину """
        self.message = None, 'B'

    def tell_joke(self):
        """ Возращает случайный анекдот """
        index = random.randint(1, len(self.jokes))
        self.message = self.jokes[str(index)], 'M'

    def update_jokes(self, new_jokes: dict):
        """ Обновление набора золотых анекдотов """
        self.jokes = new_jokes

    def big_handler(self):
        """ Здесь полномочия малой модели все, заапускаем тяжелую аретллерию """
        me_token = False
        temperature = self.start_temperature
        input_network = self.response
        answer = 'Повторите пожалуйста'

        while not me_token:
            text = self.big_model.generate(prompt=input_network,
                                           return_as_list=True,
                                           temperature=temperature)
            text = text[0].split('\n')

            if len(text) <= 1:  # убираем случаи, если не получилось сгенерить ответы
                continue

            network_reply = text[1]

            if network_reply.startswith('[me]'):
                me_token = True
                answer = network_reply
            else:
                if temperature >= self.max_temperature:
                    temperature = self.start_temperature
                    me_token = True
                    answer = 'Повторите пожалуйста'
                    # raise RuntimeError("Max temperature reached")
            temperature += 0.1

        self.message = answer.replace('[me]', ''), 'M'


if __name__ == '__main__':
    assistant = Bot()
