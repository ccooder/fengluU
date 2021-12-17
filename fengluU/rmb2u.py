#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2021/12/15 16:35
from fengluU import NFLError
import regex

__all__ = ['rmb2upper']


class RMB2U(object):
    __instance = None
    __is_first = True

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__is_first:
            RMB2U.__is_first = False
            self.__RMB_UNIT = ['万', '亿']
            self.__RMB_NUM = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']

    def append_uint(self, unit: str):
        self.__RMB_UNIT.append(unit)

    def pop_unit(self):
        self.__RMB_UNIT.pop()

    def rmb2upper(self, num: str) -> str:
        """将输入的数字按照人民币大写的书写方式返回(支持16位)
        例如：
            123456789\n
            壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖元整\n

        :param num: 人民币小写
        :return: 返回人民币大写的形式
        """

        def cal_unit(num_index: int) -> str:
            """计算对应编号数字的单位

            :param num_index: 数字的编号，指的是数字中的某一位数字在该数字中从右往左数的编号，编号从0开始\n
            :return: 返回指定编号位数字的单位
            """
            if num_index == 0:  # 如果数字为个位，没有单位
                return ''
            remain = num_index % 4
            if remain > 0:
                if remain == 1:
                    return '拾'
                elif remain == 2:
                    return '佰'
                elif remain == 3:
                    return '仟'
            else:
                quotient_4 = num_index // 4
                if quotient_4 % 2 != 0:
                    return '万'
                else:
                    bin_quotient_4 = bin(quotient_4)
                    c1_bin_quotient_4 = bin_quotient_4.split('b')[1].count('1')
                    c0_bin_quotient_4 = bin_quotient_4.split('b')[1].count('0')
                    if c1_bin_quotient_4 == 1:
                        return self.__RMB_UNIT[c0_bin_quotient_4]
                    else:
                        for check_index in range(1, len(self.__RMB_UNIT)):
                            if quotient_4 % (2 ** check_index) == 0:
                                checked_quotient_4 = quotient_4 // (2 ** check_index)
                                if checked_quotient_4 % 2 != 0:
                                    return self.__RMB_UNIT[check_index]

        # 首先验证输入的数字是否合法
        p = regex.compile(r'^(\d*)(\.?)(\d*?)$')
        if not regex.match(p, num):
            raise NFLError(f"您输入的 {num} 不是一个有效的人民币金额")

        int_part, dot, decimal_part = regex.findall(p, num)[0]
        int_part = '0' if int_part == '' else int_part
        int_part = str(int(int_part))

        if len(int_part) > 16:
            raise NFLError(f"您输入的 {num} 人民币金额大到我有点找不到北")

        if dot != '' and len(decimal_part) > 2:
            raise NFLError(f"人民币金额只支持到分哦")

        upper_num = ''
        # 首先将数字转换成单个数字的列表
        num_list = [int(str_num) for str_num in str(int_part)]
        len_num = len(num_list)
        max_len = 2 ** (len(self.__RMB_UNIT) + 2)
        if len_num > max_len:
            raise NFLError('您输入的数字太长了，我只能支持' + str(max_len) + '位数字，嘤嘤嘤')
        for i in range(len_num):
            num_bit = num_list[i]

            i_index = len_num - i - 1
            # 根据算法计算出单位
            unit = cal_unit(i_index)
            # 如果首位数字为1并且为十位，则一可不写

            # 处理该位数字是0的情况
            if num_bit == 0:
                if self.__RMB_UNIT.count(unit) == 1:
                    """数字为0,但是该位数字的单位是CN_UNIT中的一个的情况\n
                        如果前一位是零，则删除零
                            这里会有一种极端情况，如果接下的超过四位数都为零，则会出现两个单位碰到一起\n
                            如果该单位小于等于原来的单位就在末尾用零代替第二个单位
                    """
                    if upper_num.endswith('零'):
                        upper_num = upper_num.rstrip('零')
                        # 默认单位长度为一，处理单位长度大于一的情况
                        stop = -2
                        last_unit = upper_num[-1:stop:-1][::-1]
                        while not ['拾', '佰', '仟'].count(last_unit) and not self.__RMB_UNIT.count(last_unit):
                            stop -= 1
                            last_unit = upper_num[-1:stop:-1][::-1]
                        if self.__RMB_UNIT.count(last_unit):
                            if self.__RMB_UNIT.index(unit) - self.__RMB_UNIT.index(last_unit) < 1:
                                upper_num += '零'
                                continue
                    upper_num += unit
                else:  # 如果数字为零并且不在上述单位，并且前一位不是零，则加上零
                    if not upper_num.endswith('零'):
                        upper_num += self.__RMB_NUM[num_bit]
            else:  # 数字不是零的情况就加上转换后的大写数字和单位
                if not (unit == '拾' and i == 0 and num_bit == 1):  # 若首位数字为1并且该位为十位就不需要一
                    upper_num += self.__RMB_NUM[num_bit]
                upper_num += unit
        if len(upper_num) > 1:
            upper_num = upper_num.rstrip('零')

        upper_num += '元'

        if dot == '' or decimal_part == '' or decimal_part == '0' or decimal_part == '00':
            upper_num += '整'
        else:
            if len(decimal_part) == 1:
                upper_num += self.__RMB_NUM[int(decimal_part)] + '角'
            else:
                jiao = decimal_part[0]
                fen = decimal_part[-1]
                if jiao == '0':
                    upper_num += '零'
                else:
                    upper_num += self.__RMB_NUM[int(jiao)] + '角'
                if fen != '0':
                    upper_num += self.__RMB_NUM[int(fen)] + '分'
            if int_part == '0':
                upper_num = upper_num[2::].removeprefix('零')

        return upper_num


def rmb2upper(num: str) -> str:
    """将输入的数字按照人民币大写的书写方式返回(支持16位)
        例如：
            123456789\n
            壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖元整\n

        :param num: 人民币小写
        :return: 返回人民币大写的形式
        """
    rmb2u = RMB2U()
    return rmb2u.rmb2upper(num)


if __name__ == '__main__':
    sn = '.0'
    # append_uint("牛逢路")
    # pop_unit()
    print(rmb2upper(str(sn)))
