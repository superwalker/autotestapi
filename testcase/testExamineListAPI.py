#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
import warnings
from lib.GetToken import Token
import configparser as cparser
from db_fixture.mysql_db import DB

"""定义测试用例"""
testdata = os.path.join(setting.BASE_DIR,"database","DemoExamineListTestCase.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()

"""定义公共的sql"""
global testsql
testsql=ReadExcel(testdata, "Sheet1").read_row(1,6)

"""定义公共的IP域名"""
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")



@ddt.ddt
class Demo_API(unittest.TestCase):
    """xx系统-就诊人列表"""

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore", ResourceWarning)

        token = "Bearer  " + Token.get_cas_token()
        h = {

            'Authorization': token
        }
        cls.s = requests.session()
        cls.s.headers.update(h)


    @classmethod
    def tearDownClass(cls):
        pass


    @ddt.data(*testData)
    def test_api(self,data):
        # 实例化数据库
        sqldb = DB()
        #拼接URL
        data['url'] = ip + data['url']
        # 修改测试报告用例名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']
        print("******* 正在执行用例 ->{0} *********".format(data['ID']))

        '''转化body中null值为字符串null'''
        data['body']=data['body'].replace('null','"null"')

        # 发送请求
        re = SendRequests().sendRequests(self.s,data)
        self.result = re.json()

        resp=[]
        if re.status_code == 200:

            '''获取请求返回数据'''
            resp = self.result['data']
            '''获取请求返回数据总数'''
            total = self.result['total']
        else:
            pass

        sql = testsql

        '''获取商户id'''
        ID = Token.GetMerchantID()
        values = {'merchant_id': ID}

        '''判断参数是否为空，不为空则作为参数提交给sql执行'''
        # 字符串转换成字典
        body = eval(data['body'])
        code=data['status_code']

        # 获取字典指定键的值
        if body.get('search') == '' or body.get('search') is None:
            pass
        else:
            search = '%%' + body['search'] + '%%'
            sql=sql + ' and (a.user_drugs_name like "'+ search +'"  or a.phone like "'+ search +'") '

        if body.get('start_time') == '' or body.get('start_time') is None:
            pass
        else:
            values['start_time'] =  str(body['start_time'])
            values['end_time'] =  str(body['end_time'] )
            sql =sql + ' and a.created_at >= '+values['start_time']+' and a.created_at <='+values['end_time']+' '

        sql=sql+' ORDER BY a.created_at DESC'
        dbresult = sqldb.executevaluesql(sql,**values)
        sqldb.close()

        '''获取数据库第一页数据'''
        '''切片取返回值前10条数据，如果不够十条，展示所有值'''
        if len(dbresult):
            resdbid = []
            for k in dbresult:
                resdbid.append(k['id'])
            resdbid=resdbid[0:10:1]

        '''查询数据库返回总数'''
        dbtotal = len(dbresult)

        if resp and re.status_code==200 :

            '''获取请求第一条数据'''
            respon=resp[0]

            '''获取数据库返回第一条数据'''
            dbres = dbresult[0]

            '''处理断言类型格式不符'''
            dbres['created_at']=str(dbres['created_at'])

            '''处理用药人基本信息'''
            age=respon['user_drug']['age']
            sex=respon['user_drug']['sex']

            '''处理疾病列表'''
            disease_name = []
            for v in respon['disease']:
                disease_name.append(v['disease_name'])
            disease_name = ','.join(disease_name)

            '''获取第一页请求返回id'''
            resid = []
            for k in resp:
                resid.append(k['id'])


            '''接口返回与数据库查询断言'''
            self.assertEqual(respon['id'], dbres['id'], "接口返回id:%d ,数据库返回id:%d" % (respon['id'], dbres['id']))
            self.assertEqual(respon['shop_id'], dbres['shop_id'], "接口返回shop_id:%s ,数据库返回shop_id:%s" % (respon['shop_id'], dbres['shop_id']))
            self.assertEqual(respon['shop_name'], dbres['shop_name'], "接口返回shop_name:%s ,数据库返回shop_name:%s" % (respon['shop_name'], dbres['shop_name']))
            self.assertEqual(respon['user_drugs_name'], dbres['user_drugs_name'], "接口返回用药人name:%s ,数据库返回用药人name:%s" % (respon['user_drugs_name'], dbres['user_drugs_name']))
            self.assertEqual(respon['card_no'], dbres['card_no'], "接口返回身份证card_no:%s ,数据库返回身份证card_no:%s" % (respon['card_no'], dbres['card_no']))
            self.assertEqual(respon['phone'], dbres['phone'], "接口返回phone:%s ,数据库返回phone:%s" % (respon['phone'], dbres['phone']))
            self.assertEqual(respon['prescription_url'], dbres['prescription_url'], "接口返回处方图片prescription_url:%s ,数据库返回处方图片prescription_url:%s" % (respon['prescription_url'], dbres['prescription_url']))
            self.assertEqual(sex, dbres['sex'], "接口返回sex:%s ,数据库返回sex:%s" % (sex, dbres['sex']))
            self.assertEqual(age, dbres['age'], "接口返回age:%s ,数据库返回age:%s" % (age, dbres['age']))
            self.assertEqual(disease_name, dbres['disease_name'], "接口返回疾病disease_name:%s ,数据库返回疾病disease_name:%s" % (disease_name, dbres['disease_name']))
            self.assertEqual(respon['status'], dbres['status'],"接口返回状态status:%s ,数据库返回状态status:%s" % (respon['status'], dbres['status']))
            self.assertEqual(respon['created_at'], dbres['created_at'],"接口返回created_at:%s ,数据库返回created_at:%s" % (respon['created_at'], dbres['created_at']))
            self.assertEqual(respon['remark'], dbres['remark'],"接口返回remark:%s ,数据库返回uremark:%s" % (respon['remark'], dbres['remark']))

            '''请求返回code断言'''
            self.assertEqual(str(re.status_code),code , "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, code))
            print('请求返回code:' + str(re.status_code)+",预期返回code:"+str(data['status_code']))

            '''请求第一页所有id 和数据库前10条id断言'''
            self.assertListEqual(resid, resdbid, "接口返回第一页所有【id】:%s ,数据库返回所有【id】:%s" % (resid, resdbid))
            print('请求第一页所有id:'+str(resid))
            print('数据库第一页id:'+str(resdbid))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:'+str(total))
            print('数据库数据总数:'+str(dbtotal))

        elif re.status_code==200 and len(resp)==0:
            print('re.status_code==200 and len(resp)==0')

            '''无数据查询出断言'''
            resp = tuple(resp)
            self.assertEqual(resp, dbresult, "接口返回为空值：%s,数据库返回为空值：%s" % (resp, dbresult))
            print('接口返回为空：'+str(resp))
            print('数据库返回为空：'+str(dbresult))

            '''请求返回code断言'''
            self.assertEqual(str(re.status_code), code, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, code))
            print('请求返回code:' + str(re.status_code) + ",预期返回code:" + str(data['status_code']))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:'+str(total))
            print('数据库数据总数:'+str(dbtotal))

        elif re.status_code != 200 and len(resp)==0:

            print('re.status_code != 200 and len(resp)==0')
            self.assertEqual(str(re.status_code), code, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, code))
            print('请求返回code:' + str(re.status_code) + ",预期返回code:" + str(data['status_code']))

            '''请求message 断言'''
            self.assertEqual(self.result['message'], data['msg'], "接口返回【message】:%s ,预期返回【msg】:%s" % (self.result['message'], data['msg']))
            print('请求返回的message: ' + self.result['message'])
            # message="请求返回的message: " + self.result['message']
            # print(f"\033[1;34;46m{message}\033[0m")

        else:
            print('qita')





if __name__=='__main__':
    unittest.main()


