#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys

from config.setting import BASE_DIR
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
from lib.writeexcel import WriteExcel
import json
import warnings
from lib.GetToken import get_token

testdata = os.path.join(BASE_DIR,"database","PatientListApi.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()

TARGET_FILE = os.path.join(BASE_DIR,"report","excelReport","PatientListApi.xlsx")

@ddt.ddt
class Demo_API(unittest.TestCase):
    """蜜方系统-就诊人列表"""
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        token = "Bearer  " + get_token()
        h = {
            'Authorization': token
        }
        self.s = requests.session()
        self.s.headers.update(h)

    def tearDown(self):
        pass

    @ddt.data(*testData)
    def test_api(self,data):
        # 获取ID字段数值，截取结尾数字并去掉开头0
        rowNum = int(data['ID'].split("_")[1])

        # 修改测试报告用例名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']

        print("******* 正在执行用例 ->{0} *********".format(data['ID']))
        print("请求方式: {0}，请求URL: {1}".format(data['method'],data['url']))
        print("请求参数: {0}".format(data['params']))
        print("post请求body类型为：{0} ,body预期结果内容为：{1}".format(data['type'], data['body']))
        # 发送请求
        re = SendRequests().sendRequests(self.s,data)
        # 获取服务端返回的值

        self.result = re.json()

        status_code= re.status_code


        # # 获取excel表格数据的状态码和消息
        readData_code = int(data["status_code"])

        readData_body = data["body"]


        ''' json值转为list 才可以进行判断对比'''
        readData_body=json.loads(readData_body)


        if readData_code == status_code and readData_body == self.result['data']:
            OK_data = "PASS"
            print("用例测试结果:  {0}---->{1}".format(data['ID'],OK_data))
            WriteExcel(TARGET_FILE).write_data(rowNum + 1,OK_data)
        if readData_code != status_code or readData_body != self.result['data']:
            NOT_data = "FAIL"
            print("用例测试结果:  {0}---->{1}".format(data['ID'], NOT_data))
            WriteExcel(TARGET_FILE).write_data(rowNum + 1,NOT_data)

        self.assertEqual(status_code, readData_code, "返回实际结果是->:%s" % status_code)

        self.assertEqual(self.result['data'], readData_body, "返回实际结果是->:%s" % self.result['data'])



if __name__=='__main__':
    unittest.main()