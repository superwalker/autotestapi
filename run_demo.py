#!/usr/bin/python3
# _*_ coding:utf-8 _*_
__author__ = 'walker'


import os,sys
sys.path.append(os.path.dirname(__file__))
from config import setting
import unittest,time
# from lib.HTMLTestRunner import HTMLTestRunner
from lib.sendmail import send_mail
from lib.newReport import new_report
from db_fixture import test_data
from package.HTMLTestRunner import HTMLTestRunner

def add_case(test_path=setting.TEST_CASE):
    """加载所有的测试用例"""
    discover = unittest.defaultTestLoader.discover(test_path, pattern='*API.py')
    return discover

def run_case(all_case,result_path=setting.TEST_REPORT):
    """执行所有的测试用例"""



    now = time.strftime("%Y-%m-%d %H_%M_%S")
    report=now + 'result.html'
    filename = os.path.join(result_path, report)

    fp = open(filename,'wb')
    runner = HTMLTestRunner(stream=fp,title='蜜方系统接口自动化测试报告',
                            description='环境：windows 10 浏览器：chrome',
                            tester='walker')
    runner.run(all_case)
    fp.close()
    report = new_report(setting.TEST_REPORT) #调用模块生成最新的报告
    send_mail(report) #调用发送邮件模块

if __name__ =="__main__":
    cases = add_case()
    run_case(cases)
