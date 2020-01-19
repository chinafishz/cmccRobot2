
import time
import requests
from bs4 import BeautifulSoup
import random
import json
import _thread

import iot_system
import importlib as imp
import threading




def sms_4a(r, url, param, header, _proxies, _auth):
    r.post(url, data=param, headers=header, verify=False, proxies=_proxies, auth=_auth)
    _thread.exit_thread()


def login_4a_1(r, send_sms1, send_sms2, _proxies, _auth):
    cn_name = "shizhongxia"
    header = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0;  TheWorld 7)',
              'Accept': '*/*', 'Accept-Language': 'zh-CN', 'Accept-Encoding': 'gzip, deflate'}
    # sendsms2会变的
    userInfo = send_sms2

    url = 'https://4a.gmcc.net'
    result = r.get(url, headers=header, verify=False, proxies=_proxies, auth=_auth)
    soup = BeautifulSoup(result.text, 'lxml')
    loginForm1 = soup.select('#loginForm')[0].find(attrs={"name": 'random_form'}).attrs['value']
    # 获取random_form
    # 登陆界面

    url = 'https://4acasp.gmcc.net/jk.do?method=checkUserType&userId=' + cn_name
    result = r.post(url, data={'method': 'checkUserType', 'userId': cn_name}, headers=header, verify=False, proxies=_proxies,auth=_auth)
    # -----应该返回：SUCCESSG|TshizhongxiaG|T------

    url = 'https://4acasp.gmcc.net/loginForward.do?target=https://4a.gmcc.net/first.do?method=login&appCode=IAM000&sendsms=' + send_sms1
    parma = {'random_form': loginForm1, 'loginPage': '/auth/nextlogin.jsp', 'smsNameText': cn_name, 'smsName': cn_name}
    result = r.post(url, data=parma, headers=header, verify=False, proxies=_proxies, auth=_auth)
    soup = BeautifulSoup(result.text, 'lxml')
    loginForm2 = soup.select('#loginForm')[0].find(attrs={"name": 'random_form'}).attrs['value']
    parma = {'sendsms': send_sms2}
    result = r.post('https://4acasp.gmcc.net/jk.do?method=checkSMSUser&appCode=IAM000', data=parma, headers=header,verify=False, proxies=_proxies, auth=_auth)

    url = 'https://4acasp.gmcc.net/jk.do?method=checkSMSJK&target=https://4a.gmcc.net/first.do?method=login&authType=noteAuth&appCode=IAM000&loginPage=/auth/nextlogin.jsp&userInfo=' + userInfo
    r.post(url, headers=header, verify=False, proxies=_proxies, auth=_auth)
    url = 'https://4acasp.gmcc.net/sendSms.do?smsfrom=send&target=https://4a.gmcc.net/first.do?method=login&authType=noteAuth&appCode=IAM000&loginPage=/auth/nextlogin.jsp'

    # 下面这一步获取短信验证码
    _thread.start_new_thread(sms_4a, (r, url, parma, header, _proxies, _auth))
    #     这里应该要做检查
    return loginForm2


def login_4a_2(r, cn_pwd_saw, sms_pwd, loginForm2, _proxies, _auth):
    # 验证

    cn_name = "shizhongxia"
    header = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0;  TheWorld 7)',
              'Accept': '*/*', 'Accept-Language': 'zh-CN', 'Accept-Encoding': 'gzip, deflate'}
    url = 'https://4acasp.gmcc.net/loginServlet.do?target=https://4a.gmcc.net/first.do?method=login&authType=noteAuth&appCode=IAM000'
    param = {'compInfo': '', 'random_form': loginForm2, 'loginPage': '/auth/nextUserLogin.jsp', 'userName': cn_name,
             'passWord': '', 'tokenName': cn_name, 'isUsePin': 'true', 'updatePin': 'false', 'tokenpassword': '',
             'pinCode': '', 'smsName': cn_name, 'smsPwd': cn_pwd_saw, 'dynamic_smsPwd': sms_pwd, 'checkCodeTemp': '',
             'figerName': '', 'challengeName': 'cn_name', 'challegePassword': '', 'vpn': ''}
    result = r.post(url, data=param, headers=header, verify=False, proxies=_proxies, auth=_auth)

    param = {'method': 'pageQuery',
               '_gt_json': '{"recordType":"object","pageInfo":{"totalRowNum":-1,"pageSize":50,"pageNum":1,"totalPageNum":0,"startRowNum":0,"endRowNum":0},"columnInfo":[{"id":"id","header":"资源ID","fieldName":"id","fieldIndex":"id","sortOrder":null,"hidden":true,"exportable":true,"printable":true},{"id":"hasDueAcc","header":"hasDueAcc","fieldName":"hasDueAcc","fieldIndex":"hasDueAcc","sortOrder":null,"hidden":true,"exportable":true,"printable":true},{"id":"groupName","header":"资源组","fieldName":"groupName","fieldIndex":"groupName","sortOrder":null,"hidden":false,"exportable":true,"printable":true},{"id":"name","header":"资源名称","fieldName":"name","fieldIndex":"name","sortOrder":null,"hidden":false,"exportable":true,"printable":true},{"id":"ip","header":"IP地址","fieldName":"ip","fieldIndex":"ip","sortOrder":null,"hidden":false,"exportable":true,"printable":true},{"id":"restype","header":"资源类型","fieldName":"restype","fieldIndex":"restype","sortOrder":null,"hidden":true,"exportable":true,"printable":true},{"id":"appResAccountList","header":"从帐号列表","fieldName":"id","fieldIndex":"id","sortOrder":null,"hidden":false,"exportable":true,"printable":true},{"id":"ssoMode","header":"ssoMode","fieldName":"ssoMode","fieldIndex":"ssoMode","sortOrder":null,"hidden":"true","exportable":true,"printable":true},{"id":"sysResClientList","header":"登录","fieldName":"id","fieldIndex":"id","sortOrder":null,"hidden":false,"exportable":true,"printable":true},{"id":"opt","header":"操作","fieldName":"id","fieldIndex":"id","sortOrder":null,"hidden":false,"exportable":true,"printable":true}],"sortInfo":[],"filterInfo":[],"parameters":{},"action":"load"}',
               'queryName': '', 'queryIP': '', 'isQuerySubTree': '1'}
    result = r.post('https://4a.gmcc.net/page/resource/appres/appresourceQuery.do', data=param, headers=header, verify=False, proxies=_proxies, auth=_auth)
    if result.url == 'https://4a.gmcc.net/error/error.jsp':
        return None
    json2 = json.loads(result.text)
    _system_name_list = ''
    for i in json2.get('data'):
        _name = i.get('name')
        _appResAccountList = i.get('appResAccountList').split('|')[0][:-1]
        _id_num = i.get('id')
        _system_name_list = _system_name_list+_name+'|'+_appResAccountList+'|'+_id_num+";"

    return _system_name_list


def iot_login(r, _system_name_list, _proxies, _auth):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate'}

    #记录，看一下改密码后是否都是一样
    _system_name_list = '物联网系统前台|e228568c23b8443a927555a6e5a423d2|cb26fbcb34ae463fb1f9ec41ca2057a9'
    appResAccountList = _system_name_list.split('|')[1]
    id_num = _system_name_list.split('|')[2]
    r.post('https://4a.gmcc.net/page/resource/resourceQuery.do?',
           data={'method': 'isAuthDateValid', 'subaccName': 'AGZGT0000829'}, headers=header, verify=False,
           proxies=_proxies, auth=_auth)

    param = {'method': 'checkPolicy4JK', 'resId': id_num, 'resAccId': appResAccountList,
               'date': str(time.time()).replace('.', '') + str(random.randint(1, 9))}
    r.post('https://4a.gmcc.net/page/jk/sso/appJKLogin.do', data=param, headers=header, verify=False,
                     proxies=_proxies, auth=_auth)

    param = {'method': 'wantGetMACAddress', 'resId': id_num}
    r.post('https://4a.gmcc.net/sso.do', data=param, headers=header, verify=False, proxies=_proxies, auth=_auth)

    url = 'https://4a.gmcc.net/sso.do?method=appssoData&accID=' + appResAccountList + '&resID=' + id_num + '&softname=webAppByIE&date=' + str(
        time.time()).replace('.', '') + str(random.randint(1, 9))
    s = r.get(url, headers=header, allow_redirects=True, verify=False, proxies=_proxies, auth=_auth)
    return 'success', 'iot'


# =======================测试用==========================
def main_test():
    send_sms1 = ''
    send_sms2 = ''
    cn_pwd_saw = ''

    # _proxies = {'http': 'http://chinafishz:qwer1234@79d61a65dc3eb552.natapp.cc:29980',
    #             'https': 'https://chinafishz:qwer1234@79d61a65dc3eb552.natapp.cc:29980'}
    # _auth = HTTPProxyAuth('chinafishz', 'qwer1234')
    _proxies = {}
    _auth = None

    _r = requests.session()

    loginForm = login_4a_1(_r, send_sms1, send_sms2, _proxies, _auth)
    cn_sms_pwd = input()
    result = login_4a_2(_r, cn_pwd_saw, cn_sms_pwd, loginForm, _proxies, _auth)
    print(result)

    cn_iot = input()
    iot_login(_r, cn_iot, _proxies, _auth)
    iot_system.iot_status(_r, '1440058246465', _proxies, _auth)
    thread = main_test_thread(1, 'thread-1', 1, _r, _proxies, _auth)
    thread.start()


class main_test_thread(threading.Thread):
    def __init__(self, thread_id, name, counter, _r, _proxies, _auth):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self._r = _r
        self._proxies = _proxies
        self._auth = _auth

    def run(self):
        try:
            while True:
                a = input()
                if a == 'laina':
                    a = iot_system.iot_laina500(self._r,'1064891599533', self._proxies, self._auth)
                    print(a)
                elif a == 'iot':
                    imp.reload(iot_system)
                elif a == 'puk':
                    iot_system.iot_phone_query_base(self._r, '17228124669',self._proxies,self. _auth)
                    _result = iot_system.iot_puk(self._r, self._proxies, self._auth)
                    print(_result)
        except:
            pass

if __name__ == "__main__":
    main_test()

# =======================以上为测试用==========================
