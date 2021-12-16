# -*- coding: utf-8 -*-

import psycopg2
import requests
from dotenv import load_dotenv
from http.client import HTTPConnection
from requests.auth import HTTPBasicAuth


class DeliveryBot:
    """
    Класс общается с API магазина, обрабатывает строки, рекомендации пользователей
    Если короче то отвечает за алгоритмы в проекте, связанные с заказом продуктов
    """

    def __init__(self, dbname, user, password, host, auth: tuple):
        self.conn_db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        self.user_http = auth[0]
        self.pass_http = auth[1]
        self.basicAuthCredentials = HTTPBasicAuth(self.user_http, self.pass_http)
        # self.conn_http = client.

    def order_by_category(self):
        pass


if __name__ == '__main__':
    # response = urllib.request.urlopen('http://localhost:5445/search/product/{"milk"}')
    # print(response.read())
    # load_dotenv()
    # userAndPass = 'testtesttesttest'
    # headers = {'Authorization': 'Basic %s' % userAndPass}
    # connection = HTTPConnection('http://localhost:5445')
    # print(connection.request('GET', '/search/product/молоко', headers=headers))
    # #print(requests.get('http://localhost:5445/search/product/{"напиток"}').text, headers=headers)
    basicAuthCredentials = HTTPBasicAuth('testtest', 'testtest')

    print(requests.get(f'http://localhost:5445/search/product/молоко', auth=basicAuthCredentials).json())
