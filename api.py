# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from datetime import time
import datetime
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
cook_orders = []
users = []
order_id = 0
cook_time = time(0, 7, 0)
start_tokens = ['приготовь', 'приготовить', 'новый заказ']
manager_id = None          
allOrders = []

empl_list = [0, 0, 0, 0]

roles = {'crm': 4, 'менеджер': 0, 'петя': 1, 'иван': 2, 'николай': 3}

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
    global order_id
    global order_heap
    tokens = text.split()
    if tokens and (tokens[0].lower() in start_tokens):
        if (len(tokens) == 1):
            res['response']['text'] = 'Хз что готовить'
            return True
        recipe = ' '.join(tokens[1:])
        
        if (recipes.get(recipe) != None):
            timestamp = datetime.datetime.now().time()
            timestamp = time(timestamp.hour, timestamp.minute, timestamp.second)
            order_id += 1
            item = recipes.get(recipe)
            if item.second == 0:
                order = Order(order_id, recipe, time(0, 7-item.minute, 0), timestamp, "ожидает")
            else:
                order = Order(order_id, recipe, time(0, 6-item.minute, 60-item.second), timestamp, "ожидает")
            heappush(order_heap, order)
            res['response']['text'] = 'Заказ с блюдом {} добавлен в очередь!'.format(order.orderName)
            return True
    return False

def get_free_cooker():
    for i in range(1, 4):
        if empl_list[i] == 0:
            return i
    return -1

def add_task(text, res, cook_id):
    global order_heap
    if len(order_heap) == 0:
        res['response']['text'] = 'Нет текущих заказов.'
        return
    cur_order = heappop(order_heap)
    cur_order.status = 'готовится'
    heappush(cook_orders, cur_order)
    empl_list[cook_id] = cur_order.orderId
    
    res['response']['text'] = text + 'Вы выполняете заказ № :  {}.'.format(cur_order.orderId)


def check_show_orders(text, res):
    global order_heap
    global cook_orders
    orders = order_heap + cook_orders
    orders.sort()
    print (len(orders))
    if text.lower() == 'покажи очередь':
        res['response']['text'] = ''
        timestamp = datetime.datetime.now().time()
        if len(orders) == 0:
            res['response']['text'] = 'Нет заказов в системе'
            return True
        for item in orders:
            minutes = timestamp.minute-item.addTime.minute
            if minutes < 0:
                minutes += 60
            seconds = timestamp.second-item.addTime.second
            if seconds < 0:
                seconds += 60
                minutes -= 1
            res['response']['text'] += 'Блюдо: {}, время заказа: {}, время в очереди: {}, статус: {}\n'.format(item.orderName, item.addTime, time(0, minutes, seconds), item.status)
        return True
    return False


def check_end_task(text, res, cook_id):
    add_task(text, res, cook_id)
    return True


# Функция для непосредственной обsработки диалога.
def handle_dialog(req, res):
    manager_message = ''     
    user_id = req['session']['user_id']
    current_user = -1
    if req['session']['new']:
        res['response']['text'] = 'Добро пожаловать! Можете представиться?'
        sessionStorage[user_id] = {
            'suggests': [
                "crm",                     
                "менеджер",                     
                "повар1",               
                "повар2",       
                "повар3"
            ]
        }
        #TODO: Menu for customers
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    text = req['request']['original_utterance']
    
    tokens = req['request']['original_utterance'].split()
    if tokens and text.lower() in roles.keys():
        # users.append(User(user_id, roles[tokens[0].lower()], 1))                    
        current_user = roles[tokens[0].lower()]
        if current_user >= 1 and current_user <= 3 and empl_list[current_user] == 0:
            if check_end_task('', res, current_user):
                return
        res['response']['text'] = 'Поменяла пользователя'
        return 

    if check_show_orders(text, res):
        return
     
    if check_new_order(text, res):
        return
        
    if tokens:
        if text == 'не могу выполнить':
            manager_message += '' 
            res['response']['text'] = 'назовите причину'
            return

        if text == 'приступаю':
            res['response']['text'] = 'приняла'
            return            
        if text == 'нет ингредиентов':      
            res['response']['text'] = 'Ок буду согласовывать замену'
            check_end_task(res['response']['text'], res, current_user)
            return 
        if text == 'выполнил':
            empl_list[current_user] = 0
            check_end_task('', res, current_user)
            return 

    res['response']['text'] = 'Вас не понял('
    return
            
def get_user(id) :
    for user in users :
        if (user.userId == id):
            return user
    return None

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:5]
    ]
    return suggests