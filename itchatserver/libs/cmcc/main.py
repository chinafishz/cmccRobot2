
import libs.cmcc.setting as setting
import libs.cmcc.iot as iot
import libs.cmcc.cmcc_4a as cmcc_4a
from dic import ORDER_DIC


class CmccProcess:
    send_sms1 = ''
    send_sms2 = ''
    cn_pwd_saw = ''

    def __init__(self):
        auth = load_4a_auth()  # 获取登录4A的认证信息，返还NONE或者{'send_sms1':'', 'send_sms2':'', 'cn_pwd_saw':''}
        global send_sms1, send_sms2, cn_pwd_saw
        if auth is None:
            send_sms1 = input('请输入sms1')
            send_sms2 = input('请输入sms2')
            cn_pwd_saw = input('请输入密码')
        else:
            send_sms1 = auth['send_sms1']
            send_sms2 = auth['send_sms2']
            cn_pwd_saw = auth['cn_pwd_saw']

        proxy_load = setting.proxy_load() # 获取代理信息
        self.proxies = proxy_load[0]
        self.auth = proxy_load[1]

    def load_4a_auth(self):
        config = configparser.ConfigParser()
        config.read('../../config.ini', encoding='utf-8')
        section_path = dict(config.items('path'))
        setting_file_path = section_path.get('setting_file')

        try:
            config.read('../../' + setting_file_path + 'config.ini', encoding='utf-8')
            auth = dict(config.items('4a_auth'))
        except:
            auth = None
        return auth

    def main_process(self, r, raw_order):
        # raw_order的格式为：{'order_name': 命令名称, 'param_count': 参数数量, 'system': 系统名称,'actual_order': 实际命令， 1:参数1, 2:参数2……}

        if raw_order.get('system') == 'iot':
            return self.iot_system(r, raw_order)
        elif raw_order.get('system') == '4a':
            return self.cmcc4a_system(r, raw_order)


    def iot_system(self, r, raw_order):
        if iot.test_alive(r, self.proxies, self.auth) != 'alive':
            return 'error', 'iot系统没登陆，请等待管理员操作'

        if raw_order['actual_order'] == '#iot_puk':
            try:
                # 要求返回公司名称
                entityname = iot.iot_phone_query_base(r, raw_order.get(1), self.proxies, self.auth, 'name')
                puk = iot.iot_puk(r, self.proxies, self.auth)
            except:
                return 'error', raw_order.get(1) + '的puk查询失败，没有查询结果，请检查输入的号码'
            else:
                # 判断是否为白名单公司
                if entityname in ORDER_DIC['#puk']['whitelist']:
                    return 'success', '%spuk为：%s'  %(raw_order.get(1), puk)
                else:
                    return 'warning', '%spuk为：%s'  %(raw_order.get(1), puk), '【注意】%s 公司名称为：%s'  %(raw_order.get(1), entityname)

        elif raw_order['actual_order'] == '#iot_status':
            try:
                result = iot.iot_status(r, raw_order.get(1), self.proxies, self.auth)
            except:
                return 'error', '%s的状态查询失败，没有查询结果，请检查输入的号码' % raw_order.get(1) 
            else:
                return 'success', '%s状态为：%s' % (raw_order.get(1) , result)

        elif raw_order['actual_order'] == '#iot_outstanding_fees':
            try:
                result_step_1 = iot.iot_outstanding_fees_1(r, raw_order.get(1), self.proxies, self.auth)
                result = iot.iot_outstanding_fees_2(r, result_step_1, raw_order.get(1), self.proxies, self.auth)
            except:
                return 'error', '%s的余额查询失败，没有查询结果，请检查输入的号码' % raw_order.get(1)
            else:
                return 'success', '%s的余额为：%s' % (raw_order.get(1), result)

        #elif raw_order['actual_order'] == '#laina500':
            #result = iot_system.iot_laina500(r, raw_order.get(1), self.proxies, self.auth)
            #if _result == '办理完成':
              #  return 'success', raw_order.get(1) + '已经开机,但暂采用人工加流量池方式，稍后加入再回复,请谅解'
            #else:
               # return 'error', 4esult

        # # 申请开机
        # elif raw_order['actual_order'] == '#open&stop_shenqing':
        #     try:
        #         _dic = {'': ['深**徕纳智能科技有限公司'], '@146bc331344a6eedc213bed5b29fa465e26a6673b52b566f74e45fb2adf6dd9d':['all']}
        #         # 配置微信群能操作那个公司的号码的权限
        #
        #         _dic_param = _dic.get(_from_username)
        #         result =''
        #         if _dic_param is not None:
        #             _result = iot_system.iot_phone_query_base_setp1(r, raw_order.get(1), self.proxies, self.auth, 'name')
        #             s2 = _result[0]
        #             _name = _result[1]
        #             if _name in _dic_param or _dic_param == ['all']:
        #                 iot_system.iot_phone_query_base_setp2(r, s2, raw_order.get(1), self.proxies, self.auth)
        #                 result = iot_system.stop_and_open(r,'申请开机', raw_order.get(1), self.proxies, self.auth)
        #             else:
        #                 return 'error', + raw_order.get(1) + '号码所属公司与本微信群配置不一致'
        #         else:
        #             return 'error', '没配置' + raw_order.get(1) + '号码归属公司的开机权限'
        #     except:
        #         return 'error', raw_order.get(1) + '申请开机操作【失败】,请查核原因'
        #     else:
        #         return 'success', raw_order.get(1) + '申请开机' + result

        #
        # # ===========ESOP系统===========
        # elif _cmcc_system_name == 'ESOP':
        #     pass
        #
    def cmcc4a_system(self, r, raw_order):
        if raw_order['actual_order'] == '#4a_login_clone':
            global send_sms1, send_sms2
            loginForm = cmcc_4a.login_4a_1(r, send_sms1, send_sms2, self.proxies, self.auth)  # 返回值是tuple
            return 'success', '#sms %s ' % loginForm

        elif raw_order['actual_order'] == '#4a_sms':
            global cn_pwd_saw
            result = cmcc_4a.login_4a_2(r, cn_pwd_saw, raw_order.get(1), raw_order.get(2), self.proxies, self.auth) # 返回值是tuple 或者 none
            if result is None:
                return 'error', '登陆失败'
            return 'success', result.split(';')  # 直接返回结果，由main处理

        elif _actual_order == '#4a_iot':
            s = cmcc_4a.iot_login(r, raw_order.get(1), self.proxies, self.auth)
            return 'success', s




# def import_reload(a):
#     if a == "iot_system":
#         imp.reload(iot_system)
#     elif a == 'cn_system':
#         imp.reload(cn_system)


