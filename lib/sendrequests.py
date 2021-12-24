#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import os,sys,json
import requests
from lib.GetToken import Token



class SendRequests():

    # """发送请求数据"""
    def sendRequests(self,s,apiData):
        try:
            #从读取的表格中获取响应的参数作为传递

            method = apiData["method"]
            url = apiData["url"]



            if apiData["params"] == "":
                par = None
            else:
                par = eval(apiData["params"])

            # if apiData["headers"] == "":
            #     h = None
            # else:
            #
            #     h = eval(apiData["headers"])
            #

            v = False

            if apiData["body"] == "":
                body_data = None
            else:
                body_data = eval(apiData["body"])
            '''
                1.使用data参数，报文是dict类型，如果不指定headers中content-type的类型，默认application/x-www-form-urlencoded，相当于普通form表单提交的形式，
                  会将表单内的数据转换成键值对，此时数据可以从request.POST里面获取，而request.body的内容则为a=1&b=2的这种键值对形式。

                注意：即使指定content-type=application/json，request.body的值也是类似于a=1&b=2，所以并不能用json.loads(request.body.decode())得到想要的值。

                2.使用data参数，报文是str类型，如果不指定headers中content-type的类型，默认application/json
            '''

            type = apiData["type"]

            if type == "data":
                # 转化为str格式
                body = body_data
            elif type == "json":
                # 转化为json格式
                body = json.dumps(body_data)

            else:
                body = body_data

            #发送请求 data=body
            re = s.request(method=method,url=url,params=par,data=body,verify=v)
            re.elapsed.total_seconds()
            return re
        except Exception as e:
            print(e)


