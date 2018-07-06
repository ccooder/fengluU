#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2018/07/05 10:11
from typing import Any

from mysql.connector import pooling
from mysql.connector.errors import IntegrityError
import sys
from fengluU import NFLError

__all__ = ['MySQLHelper', 'QueryDict', 'QueryDictList', 'QueryOpt']


def auto_close(func):
    """
    universal auto_close decorator
    """
    
    def call_func(self, *args, **kwargs):
        cnx = self.get_cnx()
        ret = func(self, cnx=cnx, *args, **kwargs)
        cnx.close()
        return ret
    
    return call_func


class QueryOpt(object):
    REL_AND = 'AND'
    REL_OR = 'OR'
    OPT_IS = 'IS'
    OPT_IS_NOT = 'IS NOT'
    OPT_EQUAL = '='
    OPT_GT = '>'
    OPT_GTE = '>='
    OPT_LT = '<'
    OPT_LTE = '<='
    OPT_NE = '<>'


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
    
    def get_cnx(self):
        return self.__cnxpool.get_connection()
    
    @staticmethod
    def generate_where(ql: QueryDictList, params) -> str:
        where = ''
        if ql:
            for qd in ql:
                assert isinstance(qd, QueryDict)
                where += qd.rel + ' ' + qd.key + qd.opt + '%(' + qd.key + ')s '
                # params.append(qd.value)
                params.setdefault(qd.key, qd.value)
        return where
    
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
            params = {}
            ql = kwargs.get('query_list')
            if not tablename:
                raise NFLError('如果没有传sql，必须传tablename')
            sql = 'select * from ' + tablename + ' where 1=1 '
            where = MySQLHelper.generate_where(ql, params)
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
            params = {}
            ql = kwargs.get('query_list')
            if not tablename:
                raise NFLError('如果没有传sql，必须传tablename')
            sql = 'select count(*) from ' + tablename + ' where 1=1 '
            where = MySQLHelper.generate_where(ql, params)
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
                if not tablename:
                    raise NFLError('如果没有传sql，必须传tablename')
                if not ql:
                    raise NFLError('插入语句params必须有query_list<QueryDictList>字段')
                assert isinstance(ql, QueryDictList)
                sql = 'INSERT INTO ' + tablename
                names = ' ('
                values = ' VALUES ('
                for qd in ql:
                    assert isinstance(qd, QueryDict)
                    names += qd.key + ','
                    values += '%(' + qd.key + ')s,'
                    params.setdefault(qd.key, qd.value)
                names = names.rstrip(',') + ')'
                values = values.rstrip(',') + ')'
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
                updates = ''
                for ud in ul:
                    assert isinstance(ud, QueryDict)
                    updates = ud.key + '=%(' + ud.key + ')s '
                    params.setdefault(ud.key, ud.value)
                where = ' WHERE 1=1 '
                where += MySQLHelper.generate_where(ql=ql, params=params)
                print(sql + updates + where)
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
                sql = 'DELETE FROM ' + tablename + ' WHERE 1=1 '
                where = MySQLHelper.generate_where(ql=ql, params=params)
                print(sql + where)
                cursor.execute(sql + where, params)
            row = cursor.rowcount
            cnx.commit()
        except IntegrityError as e:
            print(e, file=sys.stderr)
            print(params)
        # cnx.close()
        return row
    
    def set_config(self, **config):
        self.__cnxpool = pooling.MySQLConnectionPool(pool_name='nfl_poll',
                                                     pool_size=32,
                                                     **config
                                                     )


if __name__ == '__main__':
    config = {
        'user': 'root',
        'charset': 'utf8',
        'password': 'root',
        'host': '127.0.0.1',
        'database': 'cn_area',
        'raise_on_warnings': True,
    }
    helper = MySQLHelper()
    helper.set_config(**config)
    # 首先查询省份
    # querykw = {}
    # querykw.setdefault('sql', 'select * from areas where p_code=%s')
    # querykw.setdefault('params', (410000,))
    # # querykw.setdefault('tablename', 'areas')
    # rows = helper.query(**querykw)
    # print(rows)
    # ql = QueryList()
    # qd = QueryDict()
    # qd.put(key='p_code', value=410100)
    # ql.put(qd)
    
    # querykw = {}
    # querykw.setdefault('tablename', 'areas')
    # querykw.setdefault('query_list', ql)
    # rows = helper.query(**querykw)
    # print(rows)
    
    # querykw = {}
    # querykw.setdefault('tablename', 'areas')
    # count = helper.query_count(**querykw)
    # print(count)
    
    # querykw = {}
    # querykw.setdefault('sql', 'insert into areas (code, name, level, p_code) values (1, "郑州郑州", 1, 410000)')
    # print(helper.insert(**querykw))
    
    # querykw = {}
    # querykw.setdefault('tablename', 'areas')
    # ql = QueryDictList()
    # ql.append(QueryDict(key='code', value=1))
    # ql.append(QueryDict(key='name', value='郑州郑州2'))
    # ql.append(QueryDict(key='level', value=1))
    # ql.append(QueryDict(key='p_code', value=410000))
    # querykw.setdefault('query_list', ql)
    # print(helper.insert(**querykw))
    
    # querykw = {}
    # querykw.setdefault('sql', 'update areas set name=%s where code=2')
    # querykw.setdefault('params', ('郑州1',))
    # print(helper.update(**querykw))
    
    # querykw = {}
    # querykw.setdefault('tablename', 'areas')
    # ul = QueryDictList()
    # ul.append(QueryDict(key='name', value='郑州'))
    # ql = QueryDictList()
    # ql.append(QueryDict(key='code', value=2))
    # querykw.setdefault('update_list', ul)
    # querykw.setdefault('query_list', ql)
    # print(helper.update(**querykw))
    
    # querykw = {}
    # querykw.setdefault('sql', 'DELETE FROM areas WHERE code=%s')
    # querykw.setdefault('params', (1,))
    # print(helper.delete(**querykw))
    
    # querykw = {}
    # querykw.setdefault('tablename', 'areas')
    # ql = QueryDictList()
    # ql.append(QueryDict(key='code', value=1))
    # querykw.setdefault('query_list', ql)
    # print(helper.delete(**querykw))
