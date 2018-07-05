#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2018/07/05 10:11
from mysql.connector import pooling
from mysql.connector.errors import IntegrityError
import sys


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


class MySQLHelper(object):
    """
    MySQLHelper MySQL工具类，便于数据库连接池及连接的管理和增删改查
    """
    __instance = None
    __is_first = True
    
    __config = {
        'user': 'root',
        'charset': 'utf8',
        'password': 'root',
        'host': '127.0.0.1',
        'database': 'cn_area',
        'raise_on_warnings': True,
    }
    
    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__is_first:
            self.__cnxpool = pooling.MySQLConnectionPool(pool_name='nfl_poll',
                                                         pool_size=32,
                                                         **MySQLHelper.__config
                                                         )
            MySQLHelper.__is_first = False
    
    def get_cnx(self):
        return self.__cnxpool.get_connection()
    
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
        if sql is not None:
            if '%s' in sql and not params:
                pass
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(sql)
            for row in cursor:
                result.append(row)
        else:
            pass
            # sql = 'select * from ' + kwargs['tablename']
            # where = ' where 1=1 '
            # arglist = []
            # for key, value in kwargs.items():
            #     where += 'and ' + key + '= %s '
            #     arglist.append(value)
        # cnx.close()
        return result
    
    @auto_close
    def query_count(self, cnx=None, **kwargs) -> list:
        """

        数据库小助手-查询数据的条数\n
        :param cnx: 数据连接，装饰器自动赋值
        :param kwargs: 可以识别的关键字参数：sql，如果存在，就直接使用sql进行查询
            如果不存在，那么使用指定了表名和查询字段和条件的查询方式
        \n:return: 将查询的数据以[{}]的形式返回\n
        """
        count = 0;
        # cnx = self.get_cnx()
        sql = kwargs.get('sql')
        if sql is not None:
            cursor = cnx.cursor()
            cursor.execute(sql)
            count = cursor.fetchone()[0]
        else:
            pass
            # sql = 'select * from ' + kwargs['tablename']
            # where = ' where 1=1 '
            # arglist = []
            # for key, value in kwargs.items():
            #     where += 'and ' + key + '= %s '
            #     arglist.append(value)
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
        sql = kwargs.get('sql')
        params = kwargs.get('params')
        try:
            if sql is not None:
                cursor = cnx.cursor()
                cursor.execute(sql, params)
                rowid = cursor.lastrowid
            else:
                pass
            cnx.commit()
        except IntegrityError as e:
            print(e, file=sys.stderr)
            print(params)
        
        # cnx.close()
        return row, rowid
    
    def delete(self, sql, **kwargs):
        pass
    
    def set_config(self, **config):
        self.__cnxpool.set_config(**config)


if __name__ == '__main__':
    helper = MySQLHelper()
    # 首先查询省份
    query = {'sql': 'select * from province'}
    
    rows = helper.query(**query)
    print(rows)
    helper = MySQLHelper()
    print(id(helper))
    cnx = helper.get_cnx()
    print(cnx)
