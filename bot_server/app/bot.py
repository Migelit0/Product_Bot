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

        self.start_temperature = 0.5
        self.max_temperature = 7.0

        self.message = ('', '')  # буферы для значений
        self.response = ''
        # Зачем? Потому что мы не можем возращать значения функций, которые вызывает нейронка, и давает ей аргументы
        # Почему так можно? Потому что Питон линейный и не перемутает сообщения

        self.answers = intents

        # создаем малую модель, объявляем обработчики для каждого типа сообщений
        mappings = {'greeting': self.function_greeting, 'buy': self.buy_one_thing,
        'joke': self.tell_joke, 'howreu': self.function_howareyou, 'show_bag': self.function_show_bag,
                    'goodbye': self.function_goodbye, 'empty': self.big_handler, 'whoareu': self.function_whoareu,
                    'whourcreator': self.function_whourcreator, 'thebestman': self.function_thebestman,
                    'thebestpl': self.function_thebestpl, 'meaningoflife': self.function_meaningoflife,
                    'umadeof': self.function_umadeof, 'urbrain': self.function_urbrain}

        self.small_model = GenericAssistant('app/intents.json', intent_methods=mappings,
                                            model_name="small_model")  # легкая модель на сонове тщательно написанных ответов ранее
        # тренируем модель (ибо я хз как загружать уже созданную, а дедлайн просраьт не хочется
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

    def function_greeting(self):
        """ Возращает сообщение чтобы поздороваться """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'greeting')), 'M'

    def function_whoareu(self):
        """ Возвращает сообщение кто ты """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'whoareu')), 'M'

    def function_whourcreator(self):
        """ Возвращает сообщение кто твой создатель """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'whourcreator')), 'M'

    def function_thebestman(self):
        """ Возвращает сообщение лучший человек """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'thebestman')), 'M'

    def function_thebestpl(self):
        """ Возвращает сообщение лучший язык программирования """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'thebestpl')), 'M'

    def function_meaningoflife(self):
        """ Возвращает сообщение значение жизни """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'meaningoflife')), 'M'

    def function_umadeof(self):
        """ Сообщение из чего ты сделан """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'umadeof')), 'M'

    def function_urbrain(self):
        """ Сообщение какой у тебя мозг """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'umadeof')), 'M'

    def function_howareyou(self):
        """ Отвечает как дела """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'howreu')), 'M'

    def function_goodbye(self):
        """ Возращает сообщение чтобы попрощаться """
        self.message = choice(get_messages_by_tag(self.answers['intents'], 'goodbye')), 'M'

    def buy_one_thing(self):
        """ Возращает пустое сообщение, чтобы основной код сделал заказ на продукт """
        self.message = None, 'P'

    def function_show_bag(self):
        """ Возращает пустое сообщение, чтобы основной код показал корзину корзину """
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
