#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
from lib.writeexcel import WriteExcel
import json
import warnings
from lib.GetToken import Token
import configparser as cparser
from db_fixture.mysql_db import DB

testdata = os.path.join(setting.BASE_DIR,"database","PatientListApi.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()

# TARGET_FILE = os.path.join(setting.BASE_DIR,"report","excelReport","PatientListApi.xlsx")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")

logins = {"account": "ahdsdyf",
          "password": "12345678",
          "appid": "258634629320884225",
          "cas_login_url": "http://cas-backend.lyky.xyz/auth/login",
          "app_login_url": "http://mf-backend.lyky.xyz/backend/auth/login"
            }


@ddt.ddt
class Demo_API(unittest.TestCase):
    """蜜方系统-就诊人列表"""
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        token = "Bearer  " + Token().get_cas_token(logins)
        h = {

            'Authorization': token
        }
        self.s = requests.session()
        self.s.headers.update(h)


    def tearDown(self):
        pass


    def ParamsAnalysis(self,params,remove):
        sqldb = DB()
        tablename='mf_merchant_admin'
        selectDate=['id']
        key= {'where_datas':{'account':logins['account']}}
        merchantid=sqldb.exactselect(tablename,selectDate,**key)
        where_datas = {'merchant_id':merchantid[0]['id']}
        aa = {'where_datas': where_datas}
        sqldb.close()
        # 字符串转字典
        params = eval(params)
        # 将params值加入到dictwhere_datas中
        where_datas.update(**params)

        # 删除不需要的元素
        for k in remove:
            where_datas.pop(k)

        # 判断是否存在search参数，如果不存在则去除dic元素，存在则设置参数aa['parallel']，并删除元素user_drugs_name，phone
        if 'search' in where_datas and str(where_datas['search']).strip() == '':
            where_datas.pop('search')
        else:
            where_datas['phone'] = where_datas.pop('search')
            where_datas['name'] = where_datas['phone']
            parallel = [{'name': where_datas['name'], 'phone': where_datas['phone']}]
            aa['parallel'] = parallel
            where_datas.pop('name')
            where_datas.pop('phone')

        # 固定参数 添加，这里添加可处理传值排序问题
        aa['sortkeydesc'] = 'created_at'
        # aa['limitcounts'] = where_datas.pop('limit')
        # 更新元素值
        aa['where_datas'] = where_datas

        return aa

    @ddt.data(*testData)
    def test_api(self,data):

        #拼接URL
        data['url'] = ip + data['url']
        # 修改测试报告用例名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']

        print("******* 正在执行用例 ->{0} *********".format(data['ID']))
        # 发送请求
        re = SendRequests().sendRequests(self.s,data)

        self.result = re.json()
        resp=self.result['data']

        '''获取请求返回数据总数'''
        total = self.result['total']


        '''获取数据库第一页数据'''
        remove={'page','sort','limit'}
        aa = self.ParamsAnalysis(data['body'],remove)
        sqldb = DB()
        table_name = 'mf_merchant_user_drugs'
        select_datas = ['*']
        dbresult =sqldb.MultiQuery(table_name, select_datas, **aa)

        '''切片取返回值前10条数据，如果不够十条，展示所有值'''
        if len(dbresult):
            resdbid = []
            for k in dbresult:
                resdbid.append(k['id'])
            resdbid=resdbid[0:10:1]



        '''查询数据库返回总数'''
        dbtotal = len(dbresult)
        sqldb.close()


        if resp :

            '''获取请求第一条数据'''
            respon=resp[0]

            '''获取数据库返回第一条数据'''
            dbres = dbresult[0]

            '''处理断言类型格式不符'''
            dbres['created_at']=str(dbres['created_at'])
            dbres['updated_at'] = str(dbres['updated_at'])


            '''获取第一页请求返回id'''
            resid = []
            for k in resp:
                resid.append(k['id'])



            '''接口返回与数据库查询断言'''
            self.assertEqual(respon['id'], dbres['id'], "接口返回id:%d ,数据库返回id:%d" % (respon['id'], dbres['id']))
            self.assertEqual(respon['merchant_id'], dbres['merchant_id'], "接口返回merchant_id:%s ,数据库返回merchant_id:%s" % (respon['merchant_id'], dbres['merchant_id']))
            self.assertEqual(respon['shop_id'], dbres['shop_id'], "接口返回shop_id:%s ,数据库返回shop_id:%s" % (respon['shop_id'], dbres['shop_id']))
            self.assertEqual(respon['shop_name'], dbres['shop_name'], "接口返回shop_name:%s ,数据库返回shop_name:%s" % (respon['shop_name'], dbres['shop_name']))
            self.assertEqual(respon['name'], dbres['name'], "接口返回name:%s ,数据库返回name:%s" % (respon['name'], dbres['name']))
            self.assertEqual(respon['card_no'], dbres['card_no'], "接口返回card_no:%s ,数据库返回card_no:%s" % (respon['card_no'], dbres['card_no']))
            self.assertEqual(respon['phone'], dbres['phone'], "接口返回phone:%s ,数据库返回phone:%s" % (respon['phone'], dbres['phone']))
            self.assertEqual(respon['birthday'], dbres['birthday'], "接口返回birthday:%s ,数据库返回birthday:%s" % (respon['birthday'], dbres['birthday']))
            self.assertEqual(respon['sex'], dbres['sex'], "接口返回sex:%s ,数据库返回sex:%s" % (respon['sex'], dbres['sex']))
            self.assertEqual(respon['age'], dbres['age'], "接口返回age:%s ,数据库返回age:%s" % (respon['age'], dbres['age']))
            self.assertEqual(respon['address'], dbres['address'], "接口返回address:%s ,数据库返回address:%s" % (respon['address'], dbres['address']))
            self.assertEqual(respon['use_number'], dbres['use_number'],"接口返回use_number:%s ,数据库返回use_number:%s" % (respon['use_number'], dbres['use_number']))
            self.assertEqual(respon['created_at'], dbres['created_at'],"接口返回created_at:%s ,数据库返回created_at:%s" % (respon['created_at'], dbres['created_at']))
            self.assertEqual(respon['updated_at'], dbres['updated_at'],"接口返回updated_at:%s ,数据库返回updated_at:%s" % (respon['updated_at'], dbres['updated_at']))

            # print(type(respon))
            # print(type(dbres))
            # if self.assertDictEqual(respon,dbres,"111"):
            #     print('首条数据断言成功')


            '''请求返回code断言'''
            self.assertEqual(str(re.status_code),data['status_code'] , "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, data['status_code']))
            print('请求返回code:' + str(re.status_code)+",预期返回code:"+str(data['status_code']))

            '''请求第一页所有id 和数据库前10条id断言'''
            self.assertListEqual(resid, resdbid, "接口返回第一页所有【id】:%s ,数据库返回所有【id】:%s" % (resid, resdbid))
            print('请求第一页所有id:')
            print(resid)
            print('数据库第一页id:')
            print(resdbid)
            # self.assertListEqual()

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:')
            print(total)
            print('数据库数据总数:')
            print(dbtotal)

        else:

            resp = tuple(resp)
            '''无数据查询出断言'''
            self.assertEqual(resp, dbresult, "接口返回为空值：%s,数据库返回为空值：%s" % (resp, dbresult))
            print('接口返回为空：')
            print(resp)
            print('数据库返回为空：')
            print(dbresult)


            '''请求返回code断言'''
            self.assertEqual(re.status_code, 200, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, 200))
            print('请求返回code:' + str(re.status_code))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:')
            print(total)
            print('数据库数据总数:')
            print(dbtotal)



if __name__=='__main__':
    unittest.main()


