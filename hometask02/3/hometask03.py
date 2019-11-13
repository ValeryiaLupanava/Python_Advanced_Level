"""Hometask 3"""

import yaml


DICT = {'items': ['computer', 'printer', 'keyboard', 'mouse'],
        'item price': {'computer': '200€-1000€',
                       'keyboard': '5€-50€',
                       'mouse': '4€-7€',
                       'printer': '100€-300€'},
        'items_quantity': 4}


def yaml_write(data):
    """Writing data into yaml file"""
    with open('result.yaml', 'w+', encoding='utf-8') as f_n:
        yaml.dump(data, f_n, allow_unicode=True, default_flow_style=False)

    with open('result.yaml', encoding='utf-8') as f_n:
        extracted = yaml.load(f_n, Loader=yaml.FullLoader)

    return print("Written data is equal to the read data: ", data == extracted)


yaml_write(DICT)
