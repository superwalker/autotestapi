#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
import configparser as cparser
import warnings
from lib.GetToken import Token
from db_fixture.mysql_db import DB

testdata = os.path.join(setting.BASE_DIR,"database","DemoPharmacistAPITestCase.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")
login=cf.get("logins","account")

# logins = {"account": "ahdsdyf",
#           "password": "12345678",
#           "appid": "258634629320884225",
#           "cas_login_url": "http://cas-backend.lyky.xyz/auth/login",
#           "app_login_url": "http://mf-backend.lyky.xyz/backend/auth/login"
#             }

@ddt.ddt
class Demo_API(unittest.TestCase):
    """蜜方系统-药师资质"""
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


        token = "Bearer  " + Token.get_cas_token()
        h = {

            'Authorization': token
        }
        self.s = requests.session()
        self.s.headers.update(h)



    def tearDown(self):
        pass

    @ddt.data(*testData)
    def test_api(self,data):

        data['url'] = ip + data['url']
        # 修改测试报告用例名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']


        print("******* 正在执行用例 ->{0} *********".format(data['ID']))

        # 发送请求
        re = SendRequests().sendRequests(self.s,data)
        # 获取服务端返回的值

        self.result = re.json()
        respon=self.result


        sqldb = DB()
        sql = data['headers']+"'"+str(login)+"'"
        dbresult = sqldb.executesql(sql)
        dbres = dbresult[0]


        if respon:
            '''接口返回与数据库查询断言'''
            self.assertEqual(respon['id'], dbres['id'], "接口返回id:%d ,数据库返回id:%d" % (respon['id'], dbres['id']))
            self.assertEqual(respon['merchant_id'], dbres['merchant_id'], "接口返回merchant_id:%s ,数据库返回merchant_id:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['name'], dbres['name'], "接口返回name%s ,数据库返回name:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['card_no'], dbres['card_no'], "接口返回card_no:%s ,数据库返回card_no:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['register_no'], dbres['register_no'], "接口返回register_no:%s ,数据库返回register_no:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['qualification_no'], dbres['qualification_no'], "接口返回qualification_no:%s ,数据库返回qualification_no:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['company_name'], dbres['company_name'], "接口返回company_name:%s ,数据库返回company_name:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['sign_url'], dbres['sign_url'], "接口返回电子签名sign_url:%s ,数据库返回sign_url:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['register_url'], dbres['register_url'],"接口返回执业药师资格证register_url:%s ,数据库返回register_url:%s" % (respon['id'], dbres['id']))
            self.assertEqual(respon['qualification_url'], dbres['qualification_url'],"接口返回执业药师注册证qualification_url:%s ,数据库返回qualification_url:%s" % (respon['id'], dbres['id']))
            print('数据返回值：')
            print(respon)
            print('数据库首条数据返回值：')
            print(dbres)

            '''请求返回code断言'''
            self.assertEqual(re.status_code, 200, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, 200))
            print('请求返回code:' + str(re.status_code))

        else:
            '''无数据查询出断言'''
            self.assertEqual(respon, dbresult, "接口返回为空值：%s,数据库返回为空值：%s" % (respon, dbresult))
            print('接口返回为空：' + respon)
            print('接口返回为空：' + dbresult)


            '''请求返回code断言'''
            self.assertEqual(re.status_code, 200, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, 200))
            print('请求返回code:' + str(re.status_code))









if __name__=='__main__':
    unittest.main()
