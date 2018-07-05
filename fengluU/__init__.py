# from . import sendmsg
__all__ = ['n2u', 'A', 'mysql_helper', 'NFLError']

name = "fengluU"


class A(object):
    def __init__(self):
        print('A')
    
    def __str__(self):
        return 'A cls'


class NFLError(Exception):
    pass


if __name__ == '__main__':
    print('-----A has been defined--------')
# print('__name__ is %s' % __name__)
