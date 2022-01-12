#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from config import setting
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
# from lib.writeexcel import WriteExcel
# import json
import warnings
from lib.GetToken import Token
import configparser as cparser
from db_fixture.mysql_db import DB

testdata = os.path.join(setting.BASE_DIR,"database","MerchantAdminTestCase.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()

# TARGET_FILE = os.path.join(setting.BASE_DIR,"report","excelReport","PatientListApi.xlsx")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')

ip=cf.get("sys","IP")

account=cf.get("logins","account")
password=cf.get("logins","password")
appid=cf.get("logins","appid")
cas_login_url=cf.get("logins","cas_login_url")
app_login_url=cf.get("logins","app_login_url")


@ddt.ddt
class Demo_API(unittest.TestCase):
    """蜜方系统-成员列表"""
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

    def ParamsAnalysis(self,params,remove):

        ID = Token.GetMerchantID()
        where_datas = {'merchant_id':ID}
        aa = {'where_datas': where_datas}

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

        '''获取数据库第一页id数据'''
        remove={'page','limit'}
        aa = self.ParamsAnalysis(data['body'],remove)
        sqldb = DB()
        table_name = 'mf_merchant_admin'
        select_datas = ['*']
        dbresult =sqldb.MultiQuery(table_name, select_datas, **aa)


        '''获取数据库第一条详细数据'''
        sql = data['headers']
        ID = Token.GetMerchantID()
        values = {'merchant_id': ID}


        '''判断参数是否为空，不为空则作为参数提交给sql执行'''
        body=eval(data['body'])


        # 以list形式返回字典所有的键
        if 'status' in body.keys():
            values['status'] = body['status']
        else:
            pass

        # 获取字典指定键的值
        if body.get('search') == '':
            pass
        else:
            values['search']='%'+body['search']+'%'

        ab = sqldb.executevaluesql(sql,**values)


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
            respon = resp[0]

            '''处理签名'''
            if respon['pharmacist'] is None:
                respon['sign_url']=None
            else:
                respon['sign_url'] = respon['pharmacist']['sign_url']



            '''拼接角色名称'''
            role_name=[]
            for k in respon['relation']:
                role_name.append(k['roles']['name'])

            role_name=','.join(role_name)


            '''获取数据库返回第一条数据'''
            dbres = ab[0]

            # '''处理断言类型格式不符'''
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
            self.assertEqual(respon['account'], dbres['account'], "接口返回account:%s ,数据库返回account:%s" % (respon['account'], dbres['account']))
            self.assertEqual(respon['name'], dbres['name'], "接口返回name:%s ,数据库返回name:%s" % (respon['name'], dbres['name']))
            self.assertEqual(respon['avatar'], dbres['avatar'], "接口返回avatar:%s ,数据库返回avatar:%s" % (respon['avatar'], dbres['avatar']))
            self.assertEqual(respon['phone'], dbres['phone'], "接口返回phone:%s ,数据库返回phone:%s" % (respon['phone'], dbres['phone']))
            self.assertEqual(respon['login_ip'], dbres['login_ip'], "接口返回login_ip:%s ,数据库返回login_ip:%s" % (respon['login_ip'], dbres['login_ip']))
            self.assertEqual(respon['login_time'], dbres['login_time'], "接口返回login_time:%s ,数据库返回login_time:%s" % (respon['login_time'], dbres['login_time']))
            self.assertEqual(respon['password'], dbres['password'], "接口返回password:%s ,数据库返回password:%s" % (respon['password'], dbres['password']))
            self.assertEqual(role_name, dbres['role_name'], "接口返回role_name:%s ,数据库返回role_name:%s" % (role_name, dbres['role_name']))
            self.assertEqual(respon['sign_url'], dbres['sign_url'],"接口返回sign_url:%s ,数据库返回sign_url:%s" % (respon['sign_url'], dbres['sign_url']))
            self.assertEqual(respon['status'], dbres['status'],"接口返回status:%s ,数据库返回status:%s" % (respon['status'], dbres['status']))
            self.assertEqual(respon['created_at'], dbres['created_at'],"接口返回created_at:%s ,数据库返回created_at:%s" % (respon['created_at'], dbres['created_at']))
            self.assertEqual(respon['updated_at'], dbres['updated_at'],"接口返回updated_at:%s ,数据库返回updated_at:%s" % (respon['updated_at'], dbres['updated_at']))


            '''请求返回code断言'''
            self.assertEqual(str(re.status_code),data['status_code'] , "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, data['status_code']))
            print('请求返回code:' + str(re.status_code)+",预期返回code:"+str(data['status_code']))

            '''请求第一页所有id 和数据库前10条id断言'''
            self.assertListEqual(resid, resdbid, "接口返回第一页所有【id】:%s ,数据库返回所有【id】:%s" % (resid, resdbid))
            print('请求第一页所有id:'+str(resid))
            print('数据库第一页id:'+str(resdbid))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:'+str(total))
            print('数据库数据总数:'+str(dbtotal))

        else:

            resp = tuple(resp)
            '''无数据查询出断言'''
            self.assertEqual(resp, dbresult, "接口返回为空值：%s,数据库返回为空值：%s" % (resp, dbresult))
            print('接口返回为空：'+str(resp))
            print('数据库返回为空：'+str(dbresult))


            '''请求返回code断言'''
            self.assertEqual(re.status_code, 200, "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, 200))
            print('请求返回code:' + str(re.status_code))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:'+str(total))
            print('数据库数据总数:'+str(dbtotal))



if __name__=='__main__':
    unittest.main()


