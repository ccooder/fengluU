#! /usr/bin/python
# encoding=utf-8
# Created by Fenglu Niu on 2018/06/04 09:35
from fengluU import NFLError

__all__ = ['number2upper', 'CN_UNIT']

CN_NUM = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
CN_UNIT = ['万', '亿', '兆', '京', '垓', '秭', '穰', '沟', '涧', '正', '载', '极']


def number2upper(num: int) -> str:
    """将输入的数字按照中文的书写方式返回(支持的数字长度是8192位数字)
    例如：
        123456789\n
        一亿二千三百四十五万六千七百八十九\n
        算法如下：
            算法采用的是上数法，数穷则变，就是：万万曰亿，亿亿曰兆，兆兆曰京...
            数字从右往左数，可以获取到每个数字的编号，起始编号为0\n
            用该位数字编号和4取模,若有余，余1为十，余2为百，余3为千\n
            若整除，则用该位数字编号与4整除，若结果为奇数，则该位单位为万\n
            若结果为偶数:
                1: 先判断该结果是否是2的整数次方,若是，该位单位是CN_UNIT[次方]\n
                2：若不是:从亿位开始作为检测标记位，用结果和(2^检测标记位下标)取余\n
                若能整除，并且商为奇数则单位是 CN_INIT[标记检测位下标]

        另外，我这个方法支持的数字真的非常大，我可以不判断数字长度吗？
        每添加一个更大的单位在上面的UN_UNIT列表的最后面，您就可以将当前的长度扩充一倍
    :param num: 一个整型数字
    :return: 返回数字的中文书写方式
    """
    
    def cal_unit(num_index: int) -> str:
        """计算对应编号数字的单位\n
            :param: num_index:数字的编号，指的是数字中的某一位数字在该数字中从右往左数的编号，编号从0开始\n
            :return: 返回指定编号位数字的单位
        """
        if num_index == 0:  # 如果数字为个位，没有单位
            return ''
        remain = num_index % 4
        if remain > 0:
            if remain == 1:
                return '十'
            elif remain == 2:
                return '百'
            elif remain == 3:
                return '千'
        else:
            consult_4 = num_index // 4
            if consult_4 % 2 != 0:
                return '万'
            else:
                bin_consult_4 = bin(consult_4)
                c1_bin_consult_4 = bin_consult_4.split('b')[1].count('1')
                c0_bin_consult_4 = bin_consult_4.split('b')[1].count('0')
                if c1_bin_consult_4 == 1:
                    return CN_UNIT[c0_bin_consult_4]
                else:
                    for check_index in range(1, len(CN_UNIT)):
                        if consult_4 % (2 ** check_index) == 0:
                            checked_consult_4 = consult_4 // (2 ** check_index)
                            if checked_consult_4 % 2 != 0:
                                return CN_UNIT[check_index]
    
    # 首先验证输入的数字是否合法
    if not isinstance(num, int):
        raise NFLError('您输入的数字不是整数吧，我只能支持整数，我在正在努力学习，嘤嘤嘤')
    upper_num = ''
    # 首先将数字转换成单个数字的列表
    num_list = [int(str_num) for str_num in str(num)]
    len_num = len(num_list)
    for i in range(len_num):
        num_bit = num_list[i]
        
        i_index = len_num - i - 1
        # 根据算法计算出单位
        unit = cal_unit(i_index)
        # 如果首位数字为1并且为十位，则一可不写
        
        # 处理该位数字是0的情况
        if num_bit == 0:
            if CN_UNIT.count(unit) == 1:
                """数字为0,但是该位数字的单位是CN_UNIT等中的一个的情况\n
                    如果前一位是零，则删除零
                        这里会有一种极端情况，如果接下的超过四位数都为零，则会出现两个单位碰到一起\n
                        这时候就在末尾用零代替第二个单位
                """
                if upper_num.endswith('零'):
                    upper_num = upper_num.rstrip('零')
                    if CN_UNIT.count(upper_num[-1:-2:-1]):
                        if CN_UNIT.index(unit) - CN_UNIT.index(upper_num[-1:-2:-1]) < 1:
                            upper_num += '零'
                            continue
                upper_num += unit
            else:  # 如果数字为零并且不在上述单位，并且前一位不是零，则加上零
                if not upper_num.endswith('零'):
                    upper_num += CN_NUM[num_bit]
        else:  # 数字不是零的情况就加上转换后的大写数字和单位
            if not (unit == '十' and i == 0 and num_bit == 1):  # 若首位数字为1并且该位为十位就不需要一
                upper_num += CN_NUM[num_bit]
            upper_num += unit
    if len(upper_num) > 1:
        upper_num = upper_num.rstrip('零')
    return upper_num


if __name__ == '__main__':
    print(number2upper(1230000000837836005))
