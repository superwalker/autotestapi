#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'


class SerializationList:
    """
    creat_time:2021/11/24
    author:walker

    """

    def set_key(self,key,value):

        """
        creat_time:2021/11/24
        author:walker
        params:set_key 设置单个列表key:value值  例如返回内容为单个数据列内容可使用此方法
           key：键值   value：值
           key内容为返回respond 键值名称，一般固定可以提前预设，使用列表形式传值
           value内容为返回respond 值名称，键对应的值，使用列表形式传值。
           返回结果为dict 字典内容
        """

        api_list = []

        """强制转化list中元素为字符串格式"""
        key = [str(j) for j in key]

        """强制转化list中元素为字符串格式"""
        value = [str(j) for j in value]

        """将两个list 转化成字典key-value形式"""
        api_list=dict(zip(key,value))

        # """ 将转化好的字典dict 转化为list格式方便后期断言 """
        list=[]
        for key in api_list:

            value=api_list[key]
            sqe=(key,value)
            varchar= ":".join(sqe)

            list.append(varchar)
        return list
        # return api_list

    def set_list(self,comlist):
        """
        creat_time:2021/11/24
        author:walker
        params:set_list 合并多个查询list 为一个list
            comlist:需要追加的list,

        """
        reulist=[]
        print(comlist)
        reulist.append(comlist)

        return  reulist


