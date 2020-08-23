import csv
import os
import sys
import random
import re
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict


def gen_log(path='log.log'):
    """Генерит лог-файл"""
    barrel_vol, water_vol = random.randint(50, 100), random.randint(30, 50)

    with open(path, 'w') as f:
        f.write('META DATA:\n')
        f.write(f'{barrel_vol} (объем бочки)\n')
        f.write(f'{water_vol} (текущий объем воды в бочке)\n')

        while os.path.getsize(path) < 999990:  # 1mb
            username, act_time, act, quantity = get_gen_values()

            if act == 'top up':
                if quantity <= barrel_vol - water_vol:
                    water_vol += quantity
                    act_val = 'успех'
                else:
                    act_val = 'фэйл'
            elif act == 'scoop':
                if quantity <= water_vol:
                    water_vol -= quantity
                    act_val = 'успех'
                else:
                    act_val = 'фэйл'

            string = f'{act_time}Z - [{username}] - wanna {act} {quantity}| ({act_val})\n'
            f.write(string)

def get_gen_values():
    """return tuple (username, datetime, act, quantity)"""
    get_gen_values.hours += 1
    username = f'username{random.randint(1,10)}'
    act_time = datetime.now() + timedelta(hours=get_gen_values.hours)
    act = random.choice(('top up', 'scoop'))
    quantity = random.randint(10, 50)
    return username, act_time.isoformat(timespec='milliseconds'), act, quantity
get_gen_values.hours = 0

def  main(path, first_time, last_time):
    values = OrderedDict({  # словарь со всеми значениями
        'count_scoop': 0,
        'percent_fail_scoop': '',
        'count_fail_scoop': 0,
        'scoop_vol': 0,
        'fail_scoop_vol': 0,
        'count_topup': 0,
        'percent_fail_topup': '',
        'count_fail_topup': 0,
        'topup_vol': 0,
        'fail_topup_vol': 0,
        'start_water_vol': 0,
        'finish_water_vol': 0,
    })

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print('usage')
        sys.exit()

    for i, line in enumerate(lines):
        # получаем изначальный объем воды в бочке
        if i == 2:  # 2 строка
            start_water_vol = int(re.match(r'(?P<vol>\d+)\s', line).group('vol'))
            values['start_water_vol'] += start_water_vol
            values['finish_water_vol'] += start_water_vol
            continue

        if i > 2:  # с 3 строки
            line_datetime_obj = get_datetime_obj(line)  # получаем объект даты из строки
            act, act_val, quantity = get_values_from_str(line)  # остальные значения из строки
            # обновляем информацию о тек. обЪеме воды
            if act == 'scoop' and act_val == 'успех':
                values['finish_water_vol'] -= quantity
            elif act == 'top up' and act_val == 'успех':
                values['finish_water_vol'] += quantity

            if in_time_interval(line_datetime_obj, first_time, last_time):
                if act == 'scoop':
                    values['count_scoop'] += 1
                    if act_val == 'успех':
                        values['scoop_vol'] += quantity
                    elif act_val == 'фэйл':
                        values['count_fail_scoop'] += 1
                        values['fail_scoop_vol'] += quantity
                elif act == 'top up':
                    values['count_topup'] += 1
                    if act_val == 'успех':
                        values['topup_vol'] += quantity
                    elif act_val == 'фэйл':
                        values['count_fail_topup'] += 1
                        values['fail_topup_vol'] += quantity
            
            if line_datetime_obj == last_time:  # если последняя строка в интервале
                break

    return write_csv(values)
    
def in_time_interval(time_line, first_time, last_time):
    """Возвращает true, если time_str в указанном интервале"""
    if first_time <= time_line <= last_time:
        return True
    return False

def write_csv(values):
    try:
        values['percent_fail_scoop'] = '{:.2f}'.format(values.get('count_fail_scoop') / values.get('count_scoop') * 100)
    except ZeroDivisionError:
        values['percent_fail_scoop'] = 0

    try:
        values['percent_fail_topup'] = '{:.2f}'.format(values.get('count_fail_topup') / values.get('count_topup') * 100)
    except ZeroDivisionError:
        values['percent_fail_topup'] = 0

    del values['count_fail_scoop'], values['count_fail_topup']

    with open('result.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=list(values.keys()), quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerow(values)

def get_values_from_str(string):
    """Return a tuple (act, act_val, quantity)"""
    act = re.search(r'wanna\s(?P<act>.+)\s\d', string).group('act')
    act_val = re.search(r'\((?P<act_val>\w{4,5})\)', string).group('act_val')
    quantity = re.search(r'\s(?P<quantity>\d+)\|', string).group('quantity')
    return act, act_val, int(quantity)

def get_datetime_obj(string):
    """Из переданной строки возвращает найденный объект datetime"""
    datetime_str = re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}', string).group(0)
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')

def enter_argv():
    try:
        path, first_time, last_time = sys.argv[1:4]
    except ValueError:
        try:
            path, first_time, last_time = sys.argv[1], '1970-08-21T22:17:34', '3000-08-21T22:17:34'
        except IndexError:
            print('usage')
            sys.exit()
    
    try:
        first_datetime_obj = datetime.strptime(first_time, r'%Y-%m-%dT%H:%M:%S')
        last_datetime_obj = datetime.strptime(last_time, r'%Y-%m-%dT%H:%M:%S')
    except ValueError:
        print('usage')
        sys.exit()
    
    if first_datetime_obj > last_datetime_obj:
        print('usage')
        sys.exit()

    return path, first_datetime_obj, last_datetime_obj


if __name__ == '__main__':
    path, first_datetime_obj, last_datetime_obj = enter_argv()
    main(path, first_time=first_datetime_obj, last_time=last_datetime_obj)