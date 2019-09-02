# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from datetime import time
from models import Order
from user import User
from heapq import heappush, heappop

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.

recipes = {'борщ': time(0, 2, 40), 'грибной суп':  time(0, 2, 27),
           'рис с сухофруктами и курица в томатном соусе': time(0, 3, 20),
           'яичная лапша с говядиной в соусе': time(0, 4, 56),
           'карбонара': time(0, 5, 20), 'бефстроганов': time(0, 3, 53),
               'мясная котлета с картофелем айдахо и томатным соусом': time(0, 8, 27)}

current_orders = []
order_heap = []
orders = []
users = []
order_id = 0
cook_time = time(0, 7, 0)
start_tokens = ['приготовь', 'приготовить', 'новый заказ']
manager_id = None
manager_message = ''

empl_list = [True, True, True, True]


roles = {'crm': 0, 'повар': 1, 'менеджер': 2}

from flask import Flask, request
app = Flask(__name__)
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def check_new_order(text, res):
    tokens = text.split()
    if tokens and (tokens[0].lower() in start_tokens):
        if (len(tokens) == 1):
            res['response']['text'] = 'Хз что готовить'
            return True
        recipe = ' '.join(tokens[1:])
        if (recipes.get(recipe) != None):
            item = recipes.get(recipe)
            order = Order(recipe, time(0, 6-item.minute, 60-item.second))
            heappush(order_heap, order)
            res['response']['text'] = 'Заказ добавлен в очередь!'
            return True
    return False

# def get_free_cooker():
#     for user in users:
#         if user.status and user.role == 1:
#             return user
#     return None



def check_add_task(text, res):
    if text.lower() == 'проверь заказы':
        if len(order_heap) == 0:
            res['response']['text'] = 'Нет текущих заказов.'
            return True
        cur_order = heappop(order_heap)
        cook_id = get_free_cooker()
        # cooker = get_free_cooker()
        if cooker:
            res['response']['text'] = 'Заказ {} выполняет повар {}.'.format(cur_order.orderName, cook_id)
            # res['response']['text'] = 'Заказ {} выполняет повар {}.'.format(cur_order.orderName, cooker.userId)
        else:
            res['response']['text'] = 'Все повара заняты.'
        return True
    return False
        
def add_task(res, cook_id):
    if len(order_heap) == 0:
        res['response']['text'] = 'Нет текущих заказов.'
        return
    cur_order = heappop(order_heap)
    empl_list[cook_id] = cur_order.orderId
    res['response']['text'] = 'Заказ {} выполняет повар {}.'.format(cur_order.orderName, cook_id)
    

def check_end_task(text, res):
    tokens = text.split()
    if len(tokens) != 3:
        return False
    if tokens[0] == 'свободен':
        if tokens[1] == 'повар' and tokens[2].isdigit():
            cook_id = int(tokens[2])
            if cook_id >= 1 and cook_id <= 3:
                empl_list[cook_id] = 0
                add_task(res, cook_id)
                return True
            else:
                res['response']['text'] = 'Нет такого повара.'
                return True
    return False


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Добро пожаловать! Можете представиться?'
        sessionStorage[user_id] = {
            'suggests': [
                "CRM",
                "Повар",
                "Менеджер",
            ]
        }
        #TODO: Menu for customers
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    text = req['request']['original_utterance']

    
    tokens = req['request']['original_utterance'].split()
    user = get_user(user_id)
    if tokens and tokens[0].lower() in roles.keys():
            users.append(User(user_id, roles[tokens[0].lower()], 1))
            res['response']['text'] = 'Очень приятно'
            return 
        
    if user.role == 1 :
        if tokens and tokens[0].lower() in [
            'сделал',
            'доделал',
            'все',
            'закончил',
            'готово'
        ]:
            res['response']['text'] = 'Молодец!'
            # manager_message += '\n'
            # order_id = get_order_of_cooker(user_id)
            manager_message = "Повар с айди %s закончил заказ ." % user_id # TODO: ADD concatination
            return
    if user.role == 2:
        if tokens and tokens[0].lower() == 'новости':
            res['response']['text'] = manager_message
            manager_message = ''
            return
        if tokens and text == 'список заказов':
            res['response']['text'] = 'В системе нет заказов'
            return
            
    if check_new_order(text, res):
        return
    if check_end_task(text, res):
        return
    res['response']['text'] = 'Вас не понял('
            
def get_user(id) :
    for user in users :
        if (user.userId == id):
            return user

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:3]
    ]

    return suggests
