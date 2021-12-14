# -*- coding: utf-8 -*-

import psycopg2
from http import client
import urllib.request
import requests

class DeliveryBot:
    """
    Класс общается с API магазина, обрабатывает строки, рекомендации пользователей
    Если короче то отвечает за алгоритмы в проекте, связанные с заказом продуктов
    """

    def __init__(self, dbname, user, password, host):
        self.conn_db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        # self.conn_http = client.

    def order_by_category(self):
        pass

if __name__ == '__main__':
    #response = urllib.request.urlopen('http://localhost:5445/search/product/{"milk"}')
    #print(response.read())

    print(requests.get('http://localhost:5445/search/product/{"напиток"}').text)
