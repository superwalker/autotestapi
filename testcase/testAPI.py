#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'walker'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest,requests,ddt
from lib.readexcel import ReadExcel
from lib.sendrequests import SendRequests
import json
import warnings
from lib.GetToken import Token
import configparser as cparser
from config import setting
from db_fixture.mysql_db import DB


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")

# testData = ReadExcel(setting.SOURCE_FILE, "Sheet1").read_data()
testdata = os.path.join(setting.BASE_DIR,"database","DemoAPITestCase.xlsx")
testData = ReadExcel(testdata, "Sheet1").read_data()


"""定义公共的sql"""
global testsql
testsql=ReadExcel(testdata, "Sheet1").read_row(1,6)


@ddt.ddt
class MF_API(unittest.TestCase):
    """XX系统-处方记录列表"""

    def setUp(self):

        warnings.simplefilter("ignore", ResourceWarning)

        token = "Bearer  " + Token.get_cas_token()
        h = {

            'Authorization': token
        }
        self.s = requests.session()
        self.s.headers.update(h)


    def tearDown(self):
        # sqldb.close(self)
        pass


    def ParamsAnalysis(self,params):

        ID = Token.GetMerchantID()
        where_datas = {'merchant_id':ID }
        aa = {'where_datas': where_datas}

        # 字符串转字典
        params = eval(params)
        # 将params值加入到dictwhere_datas中
        where_datas.update(**params)

        # 删除不需要的元素
        where_datas.pop('page')
        # where_datas.pop('limit')

        # 判断是否存在end_time参数，如果不存在则去除dic元素
        if str(where_datas['end_time']).strip() == '':
            where_datas.pop('end_time')

        # 判断是否存在start_time参数，如果不存在则去除dic元素，存在则设置参数aa['section']，并删除元素start_time，end_time
        if str(where_datas['start_time']).strip() == '':
            where_datas.pop('start_time')
        else:
            section = {'created_at': str(where_datas['start_time']) + "," + str(where_datas['end_time'])}
            aa['section'] = section
            where_datas.pop('start_time')
            where_datas.pop('end_time')

        # 判断是否存在status参数，如果不存在则去除dic元素
        if str(where_datas['status']).strip() == '':
            where_datas.pop('status')

        # 判断是否存在shop_id参数，如果不存在则去除dic元素
        if str(where_datas['shop_id']).strip() == '':
            where_datas.pop('shop_id')

        # 判断是否存在search参数，如果不存在则去除dic元素，存在则设置参数aa['parallel']，并删除元素user_drugs_name，phone
        if str(where_datas['search']).strip() == '':
            where_datas.pop('search')
        else:
            where_datas['phone'] = where_datas.pop('search')
            where_datas['user_drugs_name'] = where_datas['phone']
            parallel = [{'user_drugs_name': where_datas['user_drugs_name'], 'phone': where_datas['phone']}]
            aa['parallel'] = parallel
            where_datas.pop('user_drugs_name')
            where_datas.pop('phone')

        # 固定参数 添加，这里添加可处理传值排序问题
        aa['sortkeydesc'] = 'created_at'
        aa['limitcounts'] = where_datas.pop('limit')
        # 更新元素值
        aa['where_datas'] = where_datas

        return aa


    @ddt.data(*testData)
    def test_api(self,data):
        sqldb = DB()
        #修改测试报告模板名称
        self._testMethodName = data['ID'] + ':' + data['UseCase']
        data['url'] = ip + data['url']

        print("******* 正在执行用例 ->{0} *********".format(data['ID']))
        #拼接url

        '''转化body中null值为字符串null'''
        data['body'] = data['body'].replace('null', '"null"')

        # 发送请求
        re = SendRequests().sendRequests(self.s,data)

        # # 将结果进行反序列化
        self.result = re.json()

        respon=[]
        if re.status_code == 200:
            respon=self.result['data']

            '''获取请求返回数据总数'''
            total = self.result['total']


        '''获取商户id'''
        ID = Token.GetMerchantID()
        values = {'merchant_id': ID}
        sql = testsql

        '''处理参数'''
        body = eval(data['body'])


        # 获取字典指定键的值
        '''手机号或者用药人姓名'''
        if body.get('search') == '' or body.get('search') is None:
            pass
        else:
            search = '%%' + body['search'] + '%%'
            sql = sql + ' and (a.user_drugs_name like "' + search + '"  or a.phone like "' + search + '") '

        '''开始或者结束时间'''
        if body.get('start_time') == '' or body.get('start_time') is None:
            pass
        else:
            values['start_time'] = str(body['start_time'])
            values['end_time'] = str(body['end_time'])
            sql = sql + ' and a.created_at >= ' + values['start_time'] + ' and a.created_at <=' + values[
                'end_time'] + ' '

        '''处方单状态'''
        if body.get('status') =='' or body.get('status') is None:
            pass
        else:
            values['status'] = str(body['status'])
            sql=sql +'and a.status= "'+ str(values['status']) + '" '


        '''处理店铺'''
        if body.get('shop_id') =='' or body.get('shop_id') is None:
            pass
        else:
            values['shop_id'] = str(body['shop_id'])
            sql=sql +'and a.shop_id='+ values['shop_id'] + ' '

        sql = sql + ' ORDER BY a.created_at DESC'

        if len(respon) > 0 :
            print('re.status_code==200 and len(respon) > 0')
            dbresult=sqldb.executevaluesql(sql,**values)

            ''' 获取请求返回值第一条数据'''
            resp = self.result['data'][0]

            # 处理疾病名称
            disease_name = []
            for v in resp['disease']:
                disease_name.append(v['disease_name'])
            disease_name = ','.join(disease_name)


            ''' 获取数据库返回第一条数据'''
            dbres = dbresult[0]
            dbres['created_at'] = str(dbres['created_at'])

            ''' 获取请求返回的第一页id'''
            resid = []
            for k in self.result['data']:
                resid.append(k['id'])
            # 请求参数中有limit 10  所以不需要处理数据条数

            ''' 获取第一页数据库id'''
            ''' 切片取返回值前10条数据，如果不够十条，展示所有值'''
            if len(dbresult):
                resdbid = []
                for k in dbresult:
                    resdbid.append(k['id'])
                resdbid = resdbid[0:10:1]

            ''' 获取数据库查询总数据量'''
            dbtotal=len(dbresult)


            '''第一条数据字段和数据库第一条数据断言'''
            self.assertEqual(resp['id'], dbres['id'], "接口返回id:%d ,数据库返回id:%d" % (resp['id'], dbres['id']))
            self.assertEqual(resp['created_at'], dbres['created_at'], "接口返回问诊时间:%s ,数据库返回问诊时间:%s" % (resp['created_at'], dbres['created_at']))
            self.assertEqual(resp['diag_id'], dbres['diag_id'],"接口返回问诊单号diag_id:%s ,数据库返回问诊单号diag_id:%s" % (resp['diag_id'], dbres['diag_id']))
            self.assertEqual(resp['shop_name'], dbres['shop_name'],"接口返回门店名称shop_name:%s ,数据库返回门店名称shop_name:%s" % (resp['shop_name'], dbres['shop_name']))
            self.assertEqual(resp['user_drugs_name'], dbres['user_drugs_name'],"接口返回【用药人user_drugs_name】:%s ,数据库返回【用药人user_drugs_name】:%s" % (resp['user_drugs_name'], dbres['user_drugs_name']))
            self.assertEqual(resp['card_no'], dbres['card_no'],"接口返回【身份证card_no】:%s ,数据库返回身份证card_no:%s" % (resp['card_no'], dbres['card_no']))
            self.assertEqual(resp['phone'], dbres['phone'],"接口返回【手机号phone】:%s ,数据库返回【手机号phone】:%s" % (resp['phone'], dbres['phone']))
            self.assertEqual(resp['user_drug']['age'], dbres['age'],"接口返回【年龄age】:%s ,数据库返回【年龄age】:%s" % (resp['user_drug']['age'], dbres['age']))
            self.assertEqual(resp['user_drug']['sex'], dbres['sex'],"接口返回【性别sex】:%s ,数据库返回【性别sex】:%s" % (resp['user_drug']['sex'], dbres['sex']))
            self.assertEqual(disease_name, dbres['disease_name'],"接口返回【病情描述disease_name】:%s ,数据库返回【病情描述disease_name】:%s" % (disease_name, dbres['disease_name']))
            self.assertEqual(resp['status'], dbres['status'],"接口返回【订单状态status】:%s ,数据库返回【订单状态status】:%s" % (resp['status'], dbres['status']))
            self.assertEqual(resp['remark'], dbres['remark'],"接口返回【备注remark】:%s ,数据库返回【备注remark】:%s" % (resp['remark'], dbres['remark']))
            print('首条数据返回id：' + str(resp['id']) + '数据库首条数据返回id：' + str(dbres['id']))

            '''请求返回code断言'''
            self.assertEqual(re.status_code, int(data['status_code']), "接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, int(data['status_code'])))
            print('请求返回code:' + str(re.status_code) + '预期返回code:'+ data['status_code'])

            '''请求第一页所有id 和数据库前10条id断言'''
            self.assertListEqual(resid, resdbid, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (resid, resdbid))
            print('请求第一页所有id:' + str(resid) + '数据库第一页id:' + str(resdbid))

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:' + str(total) + '数据库数据总数:' + str(dbtotal))

        elif re.status_code==200 and len(respon)==0:
            print('re.status_code==200 and len(respon)==0')

            dbresult = sqldb.executevaluesql(sql, **values)
            dbtotal=len(dbresult)

            '''无数据查询出断言'''
            respon = tuple(respon)
            self.assertEqual(respon, dbresult, "接口返回为空值：%s,数据库返回为空值：%s" % (respon, dbresult))
            print('接口返回为空：' + str(respon))
            print('数据库返回为空：' + str(dbresult))

            '''请求返回code断言'''
            self.assertEqual(re.status_code, int(data['status_code']),"接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, int(data['status_code'])))
            print('请求返回code:' + str(re.status_code) + ",预期返回code:" + data['status_code'])

            '''请求返回数据总数和数据库数据总数断言'''
            self.assertEqual(total, dbtotal, "接口返回所有【id】:%s ,数据库返回所有【id】:%s" % (total, dbtotal))
            print('请求返回数据总数:' + str(total))
            print('数据库数据总数:' + str(dbtotal))

        elif re.status_code != 200 and len(respon)==0:

            print('re.status_code != 200 and len(resp)==0')

            self.assertEqual(re.status_code, int(data['status_code']),"接口返回【状态码】:%s ,预期返回【状态码】:%s" % (re.status_code, int(data['status_code'])))
            print('请求返回code:' + str(re.status_code) + ",预期返回code:" + data['status_code'])

            '''请求message 断言'''
            self.assertEqual(self.result['message'], data['msg'], "接口返回【message】:%s ,预期返回【msg】:%s" % (self.result['message'], data['msg']))
            print('请求返回的message: ' + self.result['message'])

        else:

            print('未知错误！')
            print(re.status_code)
            print(respon)
            print(len(respon))


        sqldb.close()
