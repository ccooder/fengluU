#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2020/9/2 16:05

from fengluU.mysql_helper import *


def gen_ddl(tables_test, tables_prod):
    ddl_sqls_temp = []
    diffs_test = [t for t in tables_test if t not in tables_prod]
    diffs_prod = [t for t in tables_prod if t not in tables_test]
    ddl_sqls_temp.extend(ddl_create(diffs_test))
    ddl_sqls_temp.extend(ddl_drop(diffs_prod))
    return ddl_sqls_temp
    pass


def ddl_create(diffs_test):
    ddl_create_sqls = []
    for table in diffs_test:
        ddl = helper_test.get_table_ddl(table=table)
        ddl = ddl.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS') + '# 已执行'
        helper_prod.exec_ddl(ddl=ddl)
        ddl_create_sqls.append(ddl)
    return ddl_create_sqls
    pass


def ddl_drop(diffs_prod):
    ddl_drop_sqls = []
    for table in diffs_prod:
        ddl_drop_sql = f'DROP TABLE IF EXISTS {table}'
        ddl_drop_sqls.append(ddl_drop_sql)
    return ddl_drop_sqls
    pass


def gen_alter(table: str = None):
    alter_sqls_temp = []
    fields_prod = helper_prod.get_table_fields(table=table)
    fields_test = helper_test.get_table_fields(table=table)
    alter_sqls_temp.extend(alter(table, fields_prod, fields_test))
    alter_sqls_temp.extend(alter_modify(table, fields_prod, fields_test))
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


def alter_drop(table, diffs):
    alter_drop_sqls = []
    for diff in diffs:
        key = diff.get('key')
        alter_drop_sql = f'ALTER TABLE {table} drop {key}'
        alter_drop_sqls.append(alter_drop_sql)
    return alter_drop_sqls


def interactive(table, diffs, diffs_old):
    keys = [row.get('key') for row in diffs_old]
    diffs_add = []
    diffs_change = []
    print('#\033[31m', end='')
    print('\n#接下来进入自主确认改名字段:')
    print('\033[0m', end='')
    print('#表名：', end='')
    print('\033[1;31m', end='')
    print(f'【{table}】', end='')
    print('\033[0m', end='')
    print(f',待确认字段{keys}')
    for i, diff in enumerate(diffs_old):
        prompt = ', '.join([f'\033[1;31m{i}\033[0m)、{e.get("key")}' for i, e in enumerate(diffs)])
        user_input = int(input(f'#[\033[31m{diff.get("key")}\033[0m]要改成哪个呢? {prompt}: '))
        while user_input not in range(len(diffs)):
            user_input = int(input(f'#请您不要玩花样，就输入提示中有的数字!{prompt}: '))
        diff_change = diffs.pop(user_input)
        diff_change.setdefault('old', diff.get('key'))
        diffs_change.append(diff_change)
    diffs_add.extend(diffs)
    return diffs_add, diffs_change


def alter(table, fields_prod, fields_test):
    alter_sqls = []
    diffs = [f for f in fields_test if f.get('key') not in [f.get('key') for f in fields_prod]]
    diffs_old = [f for f in fields_prod if f.get('key') not in [f.get('key') for f in fields_test]]
    delta = len(fields_test) - len(fields_prod)
    if len(diffs) == delta:
        alter_sqls.extend(alter_add(table, diffs))
    elif len(diffs) == 1:
        diffs[0].setdefault('old', diffs_old[0].get('key'))
        alter_sqls.extend(alter_change(table, diffs))
    elif delta < 0:
        alter_sqls.extend(alter_drop(table, diffs_old))
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


config_prod = {
    'user': 'king',
    'password': 'king001',
    'host': '127.0.0.1',
    'database': 'queen',
    'charset': 'utf8',
    'raise_on_warnings': True,
}

config_test = {
    'user': 'king',
    'password': 'king001',
    'host': '127.0.0.1',
    'database': 'king',
    'charset': 'utf8',
    'raise_on_warnings': True,
}

if __name__ == '__main__':
    helper_prod = MySQLHelper()
    helper_prod.set_config(**config_prod)
    helper_test = MySQLHelper()
    helper_test.set_config(**config_test)
    tables_test = helper_test.show_tables()
    tables_prod = helper_prod.show_tables()
    ddl_sqls = gen_ddl(tables_test, tables_prod)
    if ddl_sqls and len(ddl_sqls) > 0:
        print(f'\n#\033[32m生成的DDL如下:\033[0m')
        for sql in ddl_sqls:
            print(sql)

    for table in tables_test:
        alter_sqls = gen_alter(table)
        if alter_sqls and len(alter_sqls) > 0:
            print(f'\n#\033[32m表{table}生成ALTER SQL如下:\033[0m')
            for sql in alter_sqls:
                print(sql)
    pass
