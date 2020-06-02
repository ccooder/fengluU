#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2018/07/05 10:11
from typing import Any, Tuple

from mysql.connector import pooling
from mysql.connector.errors import IntegrityError
import sys

from mysql.connector.pooling import PooledMySQLConnection

from fengluU import NFLError

__all__ = ['MySQLHelper', 'QueryDict', 'QueryDictList', 'QueryOpt']


def auto_close(func):
    """
    universal auto_close decorator
    """

    def call_func(self, *args, **kwargs):
        cnx = self.get_cnx()
        ret = func(self, cnx=cnx, *args, **kwargs)
        assert isinstance(cnx, PooledMySQLConnection)
        cnx.close()
        return ret

    return call_func


class QueryOpt(object):
    REL_AND = 'AND'
    REL_OR = 'OR'
    OPT_IS = ' IS '
    OPT_IS_NOT = ' IS NOT '
    OPT_EQUAL = '='
    OPT_GT = '>'
    OPT_GTE = '>='
    OPT_LT = '<'
    OPT_LTE = '<='
    OPT_NE = '<>'
    OPT_LIKE = ' LIKE '


class QueryDict(object):

    def __init__(self, key=None, opt=QueryOpt.OPT_EQUAL, value=None, rel=QueryOpt.REL_AND):
        self.__key = key
        self.__opt = opt
        self.__value = value
        self.__rel = rel

    @property
    def key(self) -> str:
        return self.__key

    @key.setter
    def key(self, key: str) -> None:
        self.__key = key

    @property
    def opt(self) -> str:
        return self.__opt

    @opt.setter
    def opt(self, opt: str) -> None:
        self.__opt = opt

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value

    @property
    def rel(self) -> str:
        return self.__rel

    @rel.setter
    def rel(self, rel: str) -> None:
        self.__rel = rel

    def put(self, key='', opt=QueryOpt.OPT_EQUAL, value=Any, rel=QueryOpt.REL_AND) -> None:
        self.__key = key
        self.__opt = opt
        self.__value = value
        self.__rel = rel


class QueryDictList(list):
    def __init__(self):
        super().__init__()

    def put(self, qd: QueryDict) -> None:
        self.append(qd)


class MySQLHelper(object):
    """
    MySQLHelper MySQL工具类，便于数据库连接池及连接的管理和增删改查\n
        用法:
            config = {\n
                'user': '****',\n
                'charset': 'utf8',\n
                'password': '****',\n
                'host': 'mysql server host', # 127.0.0.1\n
                'database': '****',\n
                'raise_on_warnings': True,\n
            }\n
            helper = MySQLHelper()\n
            helper.set_config(**config)\n
    """
    __instance = None
    __is_first = True

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__is_first:
            MySQLHelper.__is_first = False
            self.__logging = False

    def get_cnx(self):
        return self.__cnxpool.get_connection()

    @property
    def logging(self) -> str:
        return self.logging

    @logging.setter
    def logging(self, logging: bool):
        self.__logging = logging

    @staticmethod
    def generate_where(ql: QueryDictList) -> Tuple[str, dict]:
        where = ' WHERE 1=1 '
        if ql:
            params = {qd.key: qd.value for qd in ql}
            where += ''.join([qd.rel + ' ' + qd.key + qd.opt + '%(' + qd.key + ')s ' for qd in ql])
        return where, params

    @staticmethod
    def execute(cursor=None, sql=str, params=tuple) -> str:
        if '%s' in sql:
            if not params:
                raise NFLError("如果使用sql，且sql中有占位符号,则必须传递params参数")
            else:
                cursor.execute(sql, params)
        else:
            cursor.execute(sql)

    @auto_close  # query = auto_close(query)
    def query(self, cnx=None, **kwargs) -> list:
        """

        数据库小助手-查询
        \n:param cnx: 数据连接，装饰器自动赋值
        \n:param kwargs: 可以识别的关键字参数：sql，如果存在并且含有placeholder %s,则必须存在params就直接使用sql进行查询
            如果不存在，那么使用指定了表名和查询字段和条件的查询方式
        \n:return: 将查询的数据以[{}]的形式返回\n
        """
        result = []
        # cnx = self.get_cnx()
        sql = kwargs.get('sql')
        params = kwargs.get('params')
        cursor = cnx.cursor(dictionary=True)
        if sql is not None:
            MySQLHelper.execute(cursor=cursor, sql=sql, params=params)
        else:
            tablename = kwargs.get('tablename')
            ql = kwargs.get('query_list')
            if not tablename:
                raise NFLError('如果没有传sql，必须传tablename')
            sql = 'select * from ' + tablename + ' where 1=1 '
            where, params = MySQLHelper.generate_where(ql)
            cursor.execute(sql + where, params)
        for row in cursor:
            result.append(row)
        return result

    @auto_close
    def query_count(self, cnx=None, **kwargs) -> list:
        """
        
        数据库小助手-查询数据的条数\n
        :param cnx: 数据连接，装饰器自动赋值
        :param kwargs: 可以识别的关键字参数：sql，如果存在，就直接使用sql进行查询
            如果不存在，那么使用指定了表名和查询字段和条件的查询方式
        :return: 将查询的数据以[{}]的形式返回\n
        """
        count = 0
        # cnx = self.get_cnx()
        cursor = cnx.cursor()
        sql = kwargs.get('sql')
        if sql is not None:
            MySQLHelper.execute(cursor=cursor, sql=sql)
        else:
            tablename = kwargs.get('tablename')
            ql = kwargs.get('query_list')
            if not tablename:
                raise NFLError('如果没有传sql，必须传tablename')
            sql = 'select count(*) from ' + tablename + ' where 1=1 '
            where, params = MySQLHelper.generate_where(ql)
            cursor.execute(sql + where, params)
        count = cursor.fetchone()[0]
        # cnx.close()
        return count

    @auto_close
    def insert(self, cnx=None, **kwargs) -> tuple:
        """

        数据库小助手-插入
        \n:param cnx: 数据库连接，装饰器自动赋值
        \n:param kwargs: 可以识别的关键字参数：sql，如果存在，就直接使用sql进行插入操作
            如果不存在，那么使用指定了表名和查询字段和条件的查询方式
        \n:return: 将插入的行数予以返回
        """
        row = 0
        rowid = None
        # cnx = self.get_cnx()
        cursor = cnx.cursor()
        sql = kwargs.get('sql')
        params = kwargs.get('params')
        try:
            if sql is not None:
                MySQLHelper.execute(cursor=cursor, sql=sql, params=params)
            else:
                tablename = kwargs.get('tablename')
                params = {}
                ql = kwargs.get('query_list')
                ql_list = kwargs.get('ql_list')
                if not tablename:
                    raise NFLError('如果没有传sql，必须传tablename')
                if not ql:
                    if not ql_list or not len(ql_list):
                        raise NFLError('插入语句params必须有query_list<QueryDictList>字段,或者ql_list<list<QueryDictList>>字段')

                sql = 'INSERT INTO ' + tablename
                names = ' ('
                values = ' VALUES ('
                if ql:
                    assert isinstance(ql, QueryDictList)
                    names += ','.join([qd.key for qd in ql])
                    values += ','.join(['%(' + qd.key + ')s' for qd in ql])
                    params = {qd.key: qd.value for qd in ql}
                    values += ")"
                elif ql_list:
                    names += ','.join([qd.key for qd in ql_list[0]])
                    values = ' VALUES '
                    values += ',\n'.join(['(' + ', '.join(value) + ')' for value in
                                          [['%(' + qd.key + str(i) + ')s' for qd in ql] for i, ql in
                                           enumerate(ql_list)]])
                    params = {item[0].key + str(item[1]): item[0].value for qdi in
                              [[(qd, i) for qd in ql] for i, ql in enumerate(ql_list)] for item in qdi}

                names += ")"
                print(sql + names + values)
                cursor.execute(sql + names + values, params)
            row = cursor.rowcount
            rowid = cursor.lastrowid
            cnx.commit()
        except IntegrityError as e:
            print(e, file=sys.stderr)
            print(params)
        # cnx.close()
        return row, rowid

    @auto_close
    def update(self, cnx=None, **kwargs) -> int:
        """

        数据库小助手-更新\n
        :param cnx: 数据库连接，装饰器自动赋值
        :param kwargs: 可以识别的关键字参数：sql，如果存在，就直接使用sql进行更新操作
            如果不存在，那么使用指定了表名和更新字段和条件的更新方式
        :return: 将更新的行数予以返回
        """
        row = 0
        # cnx = self.get_cnx()
        cursor = cnx.cursor()
        sql = kwargs.get('sql')
        params = kwargs.get('params')
        try:
            if sql is not None:
                MySQLHelper.execute(cursor=cursor, sql=sql, params=params)
            else:
                tablename = kwargs.get('tablename')
                params = {}
                ul = kwargs.get('update_list')
                ql = kwargs.get('query_list')
                if not tablename:
                    raise NFLError('如果没有传sql，必须传tablename')
                if not ul:
                    raise NFLError('更新语句params必须有update_list<QueryDictList>字段')
                assert isinstance(ul, QueryDictList)
                sql = 'UPDATE ' + tablename + ' SET '
                updates = ' '.join([ud.key + '=%(' + ud.key + ')s' for ud in ul])
                params = {ud.key: ud.value for ud in ul}
                where, ql_params = MySQLHelper.generate_where(ql=ql)
                params.update(ql_params)
                # print(sql + updates + where)
                cursor.execute(sql + updates + where, params)
            row = cursor.rowcount
            cnx.commit()
        except IntegrityError as e:
            print(e, file=sys.stderr)
            print(params)
        # cnx.close()
        return row

    @auto_close
    def delete(self, cnx=None, **kwargs) -> int:
        """

                数据库小助手-删除\n
                :param cnx: 数据库连接，装饰器自动赋值
                :param kwargs: 可以识别的关键字参数：sql，如果存在，就直接使用sql进行更新操作
                    如果不存在，那么使用指定了表名和条件的删除方式
                :return: 将删除的行数予以返回
                """
        row = 0
        # cnx = self.get_cnx()
        cursor = cnx.cursor()
        sql = kwargs.get('sql')
        params = kwargs.get('params')
        try:
            if sql is not None:
                MySQLHelper.execute(cursor=cursor, sql=sql, params=params)
            else:
                tablename = kwargs.get('tablename')
                params = {}
                ql = kwargs.get('query_list')
                if not tablename:
                    raise NFLError('如果没有传sql，必须传tablename')
                if not ql:
                    raise NFLError('更新语句params必须有query_list<QueryDictList>字段')
                assert isinstance(ql, QueryDictList)
                sql = 'DELETE FROM ' + tablename
                where, params = MySQLHelper.generate_where(ql=ql)
                # print(sql + where)
                cursor.execute(sql + where, params)
            row = cursor.rowcount
            cnx.commit()
        except IntegrityError as e:
            print(e, file=sys.stderr)
            print(params)
        # cnx.close()
        return row

    def set_config(self, **config):
        self.__cnxpool = pooling.MySQLConnectionPool(pool_name='nfl_pool',
                                                     pool_size=32,
                                                     **config
                                                     )


if __name__ == '__main__':
    config = {
        'user': 'king',
        'password': 'king001',
        'host': '127.0.0.1',
        'database': 'king',
        'charset': 'utf8',
        'raise_on_warnings': True,
    }
    helper = MySQLHelper()
    helper.set_config(**config)
    helper.logging = True
    # 下面是示例代码
    # Student表结构
    # +-------+-------------+------+-----+---------+----------------+
    # | Field | Type       | Null  | Key | Default | Extra          |
    # +-------+-------------+------+-----+---------+----------------+
    # | id   | int(11)     | NO   | PRI | NULL     | auto_increment |
    # | name | varchar(32) | NO   |     | NULL     |                |
    # | age | int(11)      | YES  |     | NULL     |                |
    # +-------+-------------+------+-----+---------+----------------+

    # 通过SQL查询
    # querykw = {}
    # querykw.setdefault('sql', 'select * from student where id=%s')
    # querykw.setdefault('params', (1,))
    # # querykw.setdefault('tablename', 'areas')
    # rows = helper.query(**querykw)
    # print(rows)

    # # 通过指定表名和条件查询
    # ql = QueryDictList()
    # qd = QueryDict()
    # qd.put(key='id', value=2, rel=QueryOpt.REL_AND)
    # ql.put(qd)
    # qd = QueryDict()
    # qd.put(key='name', opt=QueryOpt.OPT_LIKE, value='张%', rel=QueryOpt.REL_OR)
    # ql.put(qd)
    # qd = QueryDict()
    # qd.put(key='age', opt=QueryOpt.OPT_IS, value=None, rel=QueryOpt.REL_AND)
    # ql.put(qd)
    # querykw = {}
    # querykw.setdefault('tablename', 'student')
    # querykw.setdefault('query_list', ql)
    # rows = helper.query(**querykw)
    # print(rows)

    # 查询数量
    # querykw = {}
    # ql = QueryDictList()
    # qd = QueryDict()
    # qd.put(key='age', opt=QueryOpt.OPT_GTE, value=18)
    # ql.append(qd)
    # querykw.setdefault('tablename', 'student')
    # querykw.setdefault('query_list', ql)
    # count = helper.query_count(**querykw)
    # print(count)

    # sql添加
    # querykw = {}
    # querykw.setdefault('sql', 'insert into student (name, age) values ("张六", 19)')
    # print(helper.insert(**querykw))

    # # 指定表名和字段添加 (可批量插入)
    # querykw = {}
    # querykw.setdefault('tablename', 'student')
    # ql_list = []
    # ql = QueryDictList()
    # ql.append(QueryDict(key='name', value='赵七'))
    # ql.append(QueryDict(key='age', value=20))
    # ql_list.append(ql)
    # ql = QueryDictList()
    # ql.append(QueryDict(key='name', value='李八'))
    # ql.append(QueryDict(key='age', value=19))
    # ql_list.append(ql)
    # # 若单条添加，则添加一个ql，键值为query_list
    # querykw.setdefault('query_list', ql)
    # # 若批量添加,则添加一个ql_list,键值为ql_list
    # querykw.setdefault('ql_list', ql_list)
    # print(helper.insert(**querykw))

    # # sql更新
    # querykw = {}
    # querykw.setdefault('sql', 'update student set name=%s where id=1')
    # querykw.setdefault('params', ('张三',))
    # print(helper.update(**querykw))

    # # 指定表名和字段更新
    # querykw = {}
    # querykw.setdefault('tablename', 'student')
    # ul = QueryDictList()
    # ul.append(QueryDict(key='name', value='张三'))
    # ql = QueryDictList()
    # ql.append(QueryDict(key='id', value=1))
    # querykw.setdefault('update_list', ul)
    # querykw.setdefault('query_list', ql)
    # print(helper.update(**querykw))

    # # sql删除
    # querykw = {}
    # querykw.setdefault('sql', 'delete from student where id=%s')
    # querykw.setdefault('params', (7,))
    # print(helper.delete(**querykw))

    # # 指定表名和字段删除
    # querykw = {}
    # querykw.setdefault('tablename', 'student')
    # ql = QueryDictList()
    # ql.append(QueryDict(key='id', value=7))
    # querykw.setdefault('query_list', ql)
    # print(helper.delete(**querykw))
