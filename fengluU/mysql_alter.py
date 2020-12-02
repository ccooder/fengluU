#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2020/9/2 16:05

from fengluU.mysql_helper import *


def gen_alter(table: str = None):
    alter_sqls_temp = []
    fields_old = helper_old.get_table_fields(table=table)
    fields_new = helper_new.get_table_fields(table=table)
    alter_sqls_temp.extend(alter(table, fields_old, fields_new))
    alter_sqls_temp.extend(alter_modify(table, fields_old, fields_new))
    return alter_sqls_temp


def alter_add(table, diffs):
    alter_add_sqls = []
    for diff in diffs:
        key = diff.get('key')
        type = diff.get('type')
        null = diff.get('null')
        default = diff.get('default')
        alter_add_sql = f'ALTER TABLE {table} ADD {key} {type}{f" DEFAULT {default}" if default else ""} {null};'
        alter_add_sqls.append(alter_add_sql)
    return alter_add_sqls


def alter_change(table, diffs):
    alter_add_sqls = []
    for diff in diffs:
        old = diff.get('old')
        key = diff.get('key')
        type = diff.get('type')
        null = diff.get('null')
        default = diff.get('default')
        alter_add_sql = f'ALTER TABLE {table} CHANGE {old} {key} {type}{f" DEFAULT {default}" if default else ""} {null};'
        alter_add_sqls.append(alter_add_sql)
    return alter_add_sqls


def interactive(table, diffs, diffs_old):
    keys = [row.get('key') for row in diffs_old]
    diffs_add = []
    diffs_change = []
    print('\033[31m', end='')
    print('\n接下来进入自主确认改名字段:')
    print('\033[0m', end='')
    print('表名：', end='')
    print('\033[1;31m', end='')
    print(f'【{table}】', end='')
    print('\033[0m', end='')
    print(f',待确认字段{keys}')
    for i, diff in enumerate(diffs_old):
        prompt = ', '.join([f'\033[1;31m{i}\033[0m)、{e.get("key")}' for i, e in enumerate(diffs)])
        user_input = int(input(f'[\033[31m{diff.get("key")}\033[0m]要改成哪个呢? {prompt}: '))
        while user_input not in range(len(diffs)):
            user_input = int(input(f'请您不要玩花样，就输入提示中有的数字!{prompt}: '))
        diff_change = diffs.pop(user_input)
        diff_change.setdefault('old', diff.get('key'))
        diffs_change.append(diff_change)
    diffs_add.extend(diffs)
    return diffs_add, diffs_change


def alter(table, fields_old, fields_new):
    alter_sqls = []
    diffs = [f for f in fields_new if f.get('key') not in [f.get('key') for f in fields_old]]
    diffs_old = [f for f in fields_old if f.get('key') not in [f.get('key') for f in fields_new]]
    delta = len(fields_new) - len(fields_old)
    if len(diffs) == delta:
        alter_sqls.extend(alter_add(table, diffs))
    elif len(diffs) == 1:
        diffs[0].setdefault('old', diffs_old[0].get('key'))
        alter_sqls.extend(alter_change(table, diffs))
    else:
        diffs_add, diffs_change = interactive(table, diffs, diffs_old)
        alter_sqls.extend(alter_add(table, diffs_add))
        alter_sqls.extend(alter_change(table, diffs_change))
    return alter_sqls


def alter_modify(table, fields_old, fields_new):
    alter_modify_sqls = []
    diffs = [f for f in fields_new if f.get('key') in [f1.get('key') for f1 in fields_old if
                                                       f1.get('type') != f.get('type') or f1.get('null') != f.get(
                                                           'null') or f1.get('default') != f.get('default')]]
    for diff in diffs:
        key = diff.get('key')
        type = diff.get('type')
        null = diff.get('null')
        default = diff.get('default')
        alter_modify_sql = f'ALTER TABLE {table} MODIFY {key} {type}{f" DEFAULT {default}" if default else ""} {null};'
        alter_modify_sqls.append(alter_modify_sql)
    return alter_modify_sqls


config_old = {
    'user': 'king',
    'password': 'king001',
    'host': '127.0.0.1',
    'database': 'queen',
    'charset': 'utf8',
    'raise_on_warnings': True,
}

config_new = {
    'user': 'king',
    'password': 'king001',
    'host': '127.0.0.1',
    'database': 'king',
    'charset': 'utf8',
    'raise_on_warnings': True,
}

if __name__ == '__main__':
    helper_old = MySQLHelper()
    helper_old.set_config(**config_old)
    helper_new = MySQLHelper()
    helper_new.set_config(**config_new)
    tables = helper_old.show_tables()
    alter_sqls = gen_alter('student')
    print('\n\033[32m生成ALTER SQL如下:\033[0m')
    for sql in alter_sqls:
        print(sql)
    pass
