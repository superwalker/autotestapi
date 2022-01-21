import requests
from db_fixture.mysql_db import DB
import configparser as cparser
from config import setting
import os,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
ip=cf.get("sys","IP")

logins=cf.items('logins')

logins=dict(logins)

class Token:

    def __init__(self):

        self.logins=logins

    @classmethod
    def get_cas_token(self):
        """
        使用统一账号登录的系统，获取其token
        for example: logins = {"account": erp_account, "password": erp_password, "appid": erp_appid, "cas_login_url": erp_cas_login_url, "app_login_url": erp_app_login_url}

        :param logins[account]: 用户名, 数据类型是str
        :param logins[password]: 密码, 数据类型是str
        :param logins[appid]: 统一账号内应用的ID, 数据类型是str
        :param logins[cas_login_url]: 统一账号的登录地址, 数据类型是str
        :param logins[app_login_url]: 重定向到应用的登录地址, 数据类型是str
        """
        # print(logins)
        login_cas_data = {'account': logins["account"], 'password': logins["password"], 'appid': logins["appid"]}

        try:
            cas_token = requests.post(url=logins["cas_login_url"], data=login_cas_data).json()['token']
        except Exception as  e:
            print("失败: " + str(e))

        login_app_data = {'token': cas_token}
        app_token = requests.post(url=logins["app_login_url"], data=login_app_data).json()['token']
        return app_token

    def get_token(self, logins):

        """
        使用账户密码登录的系统，获取其token
        for example: logins = {'account': bms_account, 'password': bms_password, 'login_url': bms_url }

        :param logins[account]: 用户名, 数据类型是str
        :param logins[password]: 密码, 数据类型是str
        :param logins[login_url]: 登录地址, 数据类型是str
        """
        login_data = {'account': logins["account"], 'password': logins["password"]}
        token = requests.post(url=logins["login_url"], data=login_data).json()['token']
        return token

    def get_sms_token(self, logins):
        """
        使用账户密码加手机验证码登录的系统，获取其token
        for example: logins = {"account": store_account, "password": store_password, "phone_url": store_phone_url, "sms_url": store_sms_url, "login_url": store_login_url}

        :param logins: logins，数据类型是字典
        :param logins[account]: 用户名, 数据类型是str
        :param logins[password]: 密码, 数据类型是str
        :param logins[phone_url]: 获取手机号的地址, 数据类型是str
        :param logins[sms_url]: 获取短信验证码的地址, 数据类型是str
        :param logins[login_url]: 登录地址, 数据类型是str
        """
        phone_data = {'account': logins["account"], 'password': logins["password"]}
        phone = requests.post(url=logins["phone_url"], data=phone_data).text[1:-1]
        sms_data = {'phone': phone, 'password': logins["password"]}
        requests.post(url=logins["sms_url"], data=sms_data)
        sms_code = DB().executesql('select code from oms.oms_sms_code ORDER BY id desc LIMIT 1')[0]['code']
        login_data = {'account': logins["account"], 'password': logins["password"], 'phone': phone, 'code': sms_code}
        token = requests.post(url=logins["login_url"], data=login_data).json()['token']
        return token

    @classmethod
    def GetMerchantID(cls):
        sqldb = DB()
        tablename = 'mf_merchant_admin'
        selectDate = ['id']
        key = {'where_datas': {'account': logins['account']}}
        merchantid = sqldb.exactselect(tablename, selectDate, **key)
        sqldb.close()

        return merchantid[0]['id']

if __name__=='__main__':

    A=Token.get_cas_token()
    print(A)