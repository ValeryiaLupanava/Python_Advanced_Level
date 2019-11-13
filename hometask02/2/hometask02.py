"""Hometask 2"""

import json


def wrapper(func, args):
    """Creating wrapper for writing different orders"""
    func(*args)


def write_order_to_json(item, quantity, price, buyer, date):
    """Writing data into json file"""
    dict_to_json = {
        "item": item,
        "quantity": quantity,
        "price": price,
        "buyer": buyer,
        "data": date
    }
    with open('orders.json', encoding='utf-8') as f_f:
        data = json.load(f_f)
    data['orders'].append(dict_to_json)
    with open('orders.json', 'w', encoding='utf-8') as f_n:
        json.dump(data, f_n, sort_keys=True, indent=4, ensure_ascii=False)
    return print('done')


ORDER_1 = ['printer', '10', '6700', 'Иванов И.И.', '24.09.2017']
ORDER_2 = ['scanner', '20', '10000', 'Петров П.П.', '11.01.2018']
ORDER_3 = ['computer', '5', '40000', 'Сидоров С.С.', '2.05.2019']

wrapper(write_order_to_json, ORDER_1)
wrapper(write_order_to_json, ORDER_2)
wrapper(write_order_to_json, ORDER_3)