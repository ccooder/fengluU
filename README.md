# Fenglu's Utils for Python
## 如何使用
* `$ pip3 install fengluB`
* 在py文件中引入 `from fengluU import n2u`
* 调用 `n2u.number2upper(123456789)`
## n2u number2upper 
* 将输入的数字按照中文的书写方式返回(支持的数字长度是65536位数字)
    > 例如：<br/>
        传入：123456789<br/>
        传出：一亿二千三百四十五万六千七百八十九 
* 算法如下：
   * 算法采用的是上数法，数穷则变，即：万万曰亿，亿亿曰兆，兆兆曰京...
   * 数字从右往左数，可以获取到每个数字的编号，起始编号为0
   * 用该位数字编号和4取模,若有余，余1为十，余2为百，余3为千
   * 若整除，则用该位数字编号与4整除，若结果为奇数，则该位单位为万
   * 若结果为偶数:
        1. :  先判断该结果是否是2的整数次方,若是，该位单位是`CN_UNIT[次方]`
        2. ：若不是:从亿位开始作为检测标记位，用结果和(2^检测标记位下标)取余
           1. 若能整除，并且商为奇数则单位是 `CN_INIT[标记检测位下标]`
           2. 否则标记检测位+1
* 另外，我这个方法支持的数字真的非常大，我可以不判断数字长度吗？
    每添加一个更大的单位在上面的`CN_UNIT`列表的最后面，您就可以将当前的长度扩充一倍
    
    > 添加方法: `n2u.append_unit('更大的单位')`                                    
* 参数：
    
    > :param num: 一个整型数字
* 返回值 
    > :return: 返回数字的中文书写方式
* 用法
    > ```python
    > from fengluU import n2u
    > print(n2u(123456789))
    > $ 一亿二千三百四十五万六千七百八十九
    > ```

## rmb2u rmb2upper
* 将输入的数字按照人民币大写的书写方式返回(支持16位)
    > 例如： 
        123456789<br/>
        壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖元整
* 参数
    > :param num: 人民币小写金额
* 返回值
    > :return: 返回人民币大写的形式
* 用法
    > ```python
    > from fengluU import rmb2u
    > print(rmb2u(1234567.89))
    > $ 壹佰贰拾叁万肆仟伍佰陆拾柒元捌角玖分
    > ```

## MySQLHelper
* MySQLHelper MySQL工具类，便于数据库连接池及连接的管理和增删改查

## MySQL Alter
* MySQLAlter MYSQL对比表不同工具类，便于比较不同环境的数据库表，并生成改表语句

