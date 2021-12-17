# -*- coding: utf-8 -*-

import psycopg2
import requests
from psycopg2.extras import DictCursor
from requests.auth import HTTPBasicAuth

from models import *


class DeliveryBot:
    """
    Класс общается с API магазина, обрабатывает строки, рекомендации пользователей
    Если короче то отвечает за алгоритмы в проекте, связанные с заказом продуктов
    """

    def __init__(self, db_name, db_user, db_pass, db_host, http_auth: tuple, server_ip: str, server_port: str):
        self.conn_db = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host)
        self.user_http = http_auth[0]
        self.pass_http = http_auth[1]
        self.basicAuthCredentials = HTTPBasicAuth(self.user_http, self.pass_http)
        self.server_ip = server_ip
        self.server_port = server_port
        # self.conn_http = client.

    def request_by_category(self, category: str, user_id: int):
        """ Делает заказ, основываясь на выбранной категории и рекомендациях для данного пользователя """
        all_data = requests.get(f'http://{self.server_ip}:{self.server_port}/search/product/{category}',
                                auth=self.basicAuthCredentials).json()

        ids = [i['id'] for i in all_data]
        with self.conn_db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT product_id FROM product_recommendations WHERE product_id IN %s ORDER BY purchases_number;',
                           (tuple(ids),))

            try:
                for elem in cursor:
                    product_id = elem[0]
                    break
            except IndexError:  # не существует рекомендации на эту категорию для данного пользователя
                return NoRecommendationError

        err = requests.get(f'http://{self.server_ip}:{self.server_port}/bag/{user_id}/{product_id}',
                           auth=self.basicAuthCredentials).json()

        if err:  # отловиили ошибку (пипец го-стайл)
            return err

        with self.conn_db.cursor(cursor_factory=DictCursor) as cursor:
            # обновлем количество покупок данного товара
            cursor.execute(
                'UPDATE product_recommendations SET purchases_number = purchases_number+1 WHERE  product_id=$1;',
                (product_id,))
        self.conn_db.commit()
        return True  # все круто сделали молодцы отправляем отчет

    def get_id_by_tg(self, tg_id: int):
        """ Возращает id в системе магазина по id в телеге """


if __name__ == '__main__':
    basicAuthCredentials = HTTPBasicAuth('testtest', 'testtest')

    #print(requests.get(f'http://localhost:5445/search/product/молоко', auth=basicAuthCredentials).json())
    test = DeliveryBot('shop_server', 'shop_server', 'IAmPostgresUser', 'migelit0.online', ('testtest', 'testtest'),
                       'localhost', '5445')

    print(test.request_by_category('молоко', 1))
