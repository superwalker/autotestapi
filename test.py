
import unittest
from ddt import ddt, data, unpack
'''
    1、导入ddt相关包：from ddt import ddt, data, unpack
    2、类上添加unittest.TestCase作用于测试用例上，和unittest一起使用
'''


@ddt
class Testddt(unittest.TestCase):
    def setUp(self):
        pass

    '''结果运行三次'''
    @data(12, 13, 14)
    def test_1(self, value):
        print(value)

    '''结果运行一次，出(12,13,14)'''
    @data((12, 13, 14))
    def test_2(self, value):
        print(value)

    '''结果运行一次，输出12,13,14
       参数个数看的是元祖里面的个数
    '''
    @data((12, 13, 14))
    @unpack
    def test_3(self, value1, value2, value3):
        print(value1, value2, value3)

    '''结果运行3次，分别输出(3, 2)  (4, 3) (5, 3)'''
    @data((3, 2), (4, 3), (5, 3))
    def test_4(self, value):
        print(value)

    @data((3, 2), (4, 3), (5, 3))
    @unpack
    def test_5(self, value1, value2):
        print(value1,value2)

    @data([3, 2], [4, 3], [5, 3])
    def test_6(self, value1):
        print(value1)

    @data([3, 2], [4, 3], [5, 3])
    @unpack
    def test_7(self, value1, value2):
        print(value1,value2)

    @data({'first': 1, 'second': 3, 'third': 2},{'first': 4, 'second': 6, 'third': 5})
    def test_8(self, value1):
        print(value1)

    '''
    字典拆包，参数需要和key名称一致，分别对应key值输出1 3 2
    '''
    @data({'first': 1, 'second': 3, 'third': 2})
    @unpack
    def test_9(self, first, second, third):
        print(first, second, third)