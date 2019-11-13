"""Hometask 1"""

import re
import pandas as pd


def get_data():
    """Extracting data from files"""
    params = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    file_names = ['info_1.txt', 'info_2.txt', 'info_3.txt']

    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    for file in file_names:
        with open(file, encoding='utf-8') as con:
            text = con.read()
        rows = re.split(r'\n', text)

        for row in rows:
            new = re.split(r'  +', row)
            if re.search(params[0], new[0]):
                os_prod_list.append(new[1].rstrip())
            elif re.search(params[1], new[0]):
                os_name_list.append(new[1].rstrip())
            elif re.search(params[2], new[0]):
                os_code_list.append(new[1].rstrip())
            elif re.search(params[3], new[0]):
                os_type_list.append(new[1].rstrip())

    data_tuple = list(zip(os_prod_list, os_name_list, os_code_list, os_type_list))
    main_data = pd.DataFrame(data_tuple, columns=params)
    return main_data


def write_to_csv(csv_file):
    """Writing data into csv file"""
    result = get_data()
    result.to_csv(csv_file)


write_to_csv('result.csv')
