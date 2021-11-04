import requests
from config import setting

def get_token():
    """

    :return: 返回统一账号信息登录方式
    """
    login_cas_data = {'account':setting.LOGIN_ACCOUNT,
                      'password': setting.LOGIN_PWD,
                      'appid': setting.LOGIN_APPID}

    cas_token = requests.post(url=setting.LOGIN_URL, data=login_cas_data).json()['token']
    # login_url = login_cas_data_url
    login_data = {'token': cas_token}
    return requests.post(url=setting.LOGIN_TOKEN_URL, data=login_data).json()['token']

