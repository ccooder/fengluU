# from . import sendmsg
import time

__all__ = ['n2u', 'A', 'mysql_helper', 'NFLError', 'mysql_alter']

name = "fengluU"


class A(object):
    def __init__(self):
        print('A')

    def __str__(self):
        return 'A cls'


class NFLError(Exception):
    pass


def exec_time(func):
    def decorator(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        print('function %s\'s execute_time: %ss' % (func.__name__, end - start))
        return ret

    return decorator


if __name__ == '__main__':
    print('-----A has been defined--------')
# print('__name__ is %s' % __name__)
