#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
import json
import warnings
from lib.getToken import Token
import configparser as cparser
from config import setting
from db_fixture.mysql_db import DB


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")

testData = ReadExcel(setting.SOURCE_FILE, "Sheet1").read_data()


@ddt.ddt
class MF_API(unittest.TestCase):
    """蜜方系统-处方记录列表"""

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

        logins = {"account": "ahdsdyf",
                  "password": "12345678",
                  "appid": "258634629320884225",
                  "cas_login_url": "http://cas-backend.lyky.xyz/auth/login",
                  "app_login_url": "http://mf-backend.lyky.xyz/backend/auth/login"
                    }

        token = "Bearer  " + Token().get_cas_token(logins)
        h = {

            'Authorization': token
        }
        self.s = requests.session()
        self.s.headers.update(h)



    def tearDown(self):
        # sqldb.close(self)
        pass

    @ddt.data(*testData)
    def test_api(self,data):
        # 获取ID字段数值，截取结尾数字并去掉开头0
        # rowNum = int(data['ID'].split("_")[1])
        # 修改测试报告用例名称
        # self.__module__="蜜方测试"

        # # 状态码
        #   self.result['status_code']= re.status_code
        # # 接口请求响应时间
        #   # print(re.elapsed)
        # #接口请求返回大小
        #   print(len(re.content))

        #修改测试报告模板名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']
        data['url'] = ip + data['url']

        print("******* 正在执行用例 ->{0} *********".format(data['ID']))
        #拼接url

        # 发送请求
        re = SendRequests().sendRequests(self.s,data)

        # # 将结果进行反序列化
        self.result = re.json()



        # '''实例化数据库'''


        ''' 获取请求返回值第一条数据'''
        resp=self.result['data'][0]

        # 处理病症描述字段
        disease_name = []
        for v in resp['disease']:
            disease_name.append(v['disease_name'])
        disease_name = ','.join(disease_name)

        '''
        获取数据库返回第一条数据
        '''
        sqldb = DB()
        sql = data['headers']
        dbresult=sqldb.executesql(sql)
        dbres=dbresult[0]
        dbres['created_at']=str(dbres['created_at'])



        '''
        获取请求返回的所有id
        '''
        resid = []
        for k in self.result['data']:
            resid.append(k['id'])

        '''
        获取前十条数据库id
        '''
        table_name='mf_order'
        select_datas=['id']
        aa={'where_datas':{'merchant_id':'31'},'sortkeydesc':'created_at','limitcounts':10}
        dbid=sqldb.exactselect(table_name,select_datas,**aa)

        resdbid=[]
        for k in dbid:
            resdbid.append(k['id'])
        # print(resdbid)


        '''获取数据库查询总数据量'''
        select_datas1 = ['count(*)']
        aa = {'where_datas': {'merchant_id': '31'}}
        dbtotal = sqldb.exactselect(table_name, select_datas1, **aa)
        dbtotal = dbtotal[0]['count(*)']

        '''获取请求返回数据总数'''
        total=self.result['total']




        '''第一条数据字段和数据库第一条数据断言'''
        self.assertEqual(resp['id'],dbres['id'],"接口返回id:%d ,数据库返回id:%d" % (resp['id'],dbres['id']))
        self.assertEqual(resp['created_at'], dbres['created_at'], "接口返回问诊时间:%s ,数据库返回问诊时间:%s" % (resp['created_at'], dbres['created_at']))
        self.assertEqual(resp['diag_id'], dbres['diag_id'], "接口返回问诊单号diag_id:%s ,数据库返回问诊单号diag_id:%s" % (resp['diag_id'], dbres['diag_id']))
        self.assertEqual(resp['shop_name'], dbres['shop_name'], "接口返回门店名称shop_name:%s ,数据库返回门店名称shop_name:%s" % (resp['shop_name'], dbres['shop_name']))
        self.assertEqual(resp['user_drugs_name'], dbres['user_drugs_name'], "接口返回【用药人user_drugs_name】:%s ,数据库返回【用药人user_drugs_name】:%s" % (resp['user_drugs_name'], dbres['user_drugs_name']))
        self.assertEqual(resp['card_no'], dbres['card_no'], "接口返回【身份证card_no】:%s ,数据库返回身份证card_no:%s" % (resp['card_no'], dbres['card_no']))
        self.assertEqual(resp['phone'], dbres['phone'], "接口返回【手机号phone】:%s ,数据库返回【手机号phone】:%s" % (resp['phone'], dbres['phone']))
        self.assertEqual(resp['user_drug']['age'], dbres['age'],"接口返回【年龄age】:%s ,数据库返回【年龄age】:%s" % (resp['user_drug']['age'], dbres['age']))
        self.assertEqual(resp['user_drug']['sex'], dbres['sex'], "接口返回【性别sex】:%s ,数据库返回【性别sex】:%s" % (resp['user_drug']['sex'], dbres['sex']))
        self.assertEqual(disease_name, dbres['disease_name'], "接口返回【病情描述disease_name】:%s ,数据库返回【病情描述disease_name】:%s" % (disease_name, dbres['disease_name']))
        self.assertEqual(resp['status'], dbres['status'], "接口返回【订单状态status】:%s ,数据库返回【订单状态status】:%s" % (resp['status'], dbres['status']))
        self.assertEqual(resp['remark'], dbres['remark'], "接口返回【备注remark】:%s ,数据库返回【备注remark】:%s" % (resp['remark'], dbres['remark']))

        '''请求返回code断言'''
        self.assertEqual(re.status_code, 200,"接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, 200))

        '''请求第一页所有id 和数据库前10条id断言'''
        self.assertEqual(resid, resdbid, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (resid, resdbid))

        '''请求返回数据总数和数据库数据总数断言'''
        self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))





if __name__=='__main__':

    unittest.main()

