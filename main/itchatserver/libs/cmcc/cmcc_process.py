import sys
import general_setting
from bs4 import BeautifulSoup
import importlib as imp
import requests
import iot_system

sys.path.append("../..")
from dic import ORDER_DIC



send_sms1 = ''
send_sms2 = ''
cn_pwd_saw = ''


class CmccProcess:
    def __init__(self):
        self.proxies = general_setting.proxy_load()[0]
        self.auth = general_setting.proxy_load()[1]

    def main_process(self, r, raw_order):
        # raw_order的格式为：{'order_name': 命令名称, 'param_count': 参数数量, 'system': 系统名称,'actual_order': 实际命令， 1:参数1, 2:参数2……}

        if raw_order.get('system') == 'iot':
            return self.iot_system(r, raw_order)

    def iot_system(self, r, raw_order):
        if iot_system.test_alive(r, self.proxies, self.auth) != 'alive':
            return ['error', 'iot系统没登陆，请等待管理员操作']

        if raw_order['actual_order'] == '#iot_puk':
                try:
                    # 要求返回公司名称
                    entityName =iot_system.iot_phone_query_base(r, raw_order.get(1), self.proxies, self.auth, 'name')
                    puk = iot_system.iot_puk(r, self.proxies, self.auth)
                except:
                    return 'error', raw_order.get(1) + '的puk查询失败，没有查询结果，请检查输入的号码'
                else:
                    # 判断是否为白名单公司
                    if entityName in ORDER_DIC['#puk']['whitelist']:
                        return 'success', '%spuk为：%s'  %(raw_order.get(1), puk)
                    else:
                        return 'warning', '%spuk为：%s'  %(raw_order.get(1), puk), '%s 公司名称为：%s'  %(raw_order.get(1), entityName)

        elif raw_order['actual_order'] == '#iot_status':
            try:
                result = iot_system.iot_status(r, raw_order.get(1), self.proxies, self.auth)
            except:
                return 'error', '%s的状态查询失败，没有查询结果，请检查输入的号码' % raw_order.get(1) 
            else:
                return 'success', '%s状态为：%s' % (raw_order.get(1) , result)


        elif raw_order['actual_order'] == '#iot_outstanding_fees':
            try:
                result_step_1 = iot_system.iot_outstanding_fees_1(r, raw_order.get(1), self.proxies, self.auth)
                result = iot_system.iot_outstanding_fees_2(r, result_step_1, raw_order.get(1), self.proxies, self.auth)
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
        # elif _cmcc_system_name == '4a':
        #     if _actual_order == '#4a_sms':
        #         _result = cn_system.login_4a_2(r, cn_pwd_saw, raw_order.get(1), raw_order.get(2), self.proxies,
        #                                        self.auth)
        #         # login_4a_2(r, cn_pwd_saw, sms_pwd, loginForm2, self.proxies, self.auth)
        #         # 返回值是tuple 或者 none
        #         if _result is None:
        #             return 'error', '登陆失败'
        #         del self.order_list[_from_username][_order_name]
        #         return '4a_login_up_success', _result
        #         # 直接返回结果，由main处理
        #
        #     elif _actual_order == '#4a_iot':
        #         s = cn_system.iot_login(r, raw_order.get(1), self.proxies, self.auth)
        #         # iot_login(r, _system_name_id, self.proxies, self.auth)
        #
        #         if self.config_list.setdefault('iot_loginning',0) == 1:
        #             self.config_list['iot_loginning'] = 0
        #         del self.order_list[_from_username][_order_name]
        #         return 'iot_login_up', 1
        #     elif _actual_order == '#4a_login_clone':
        #         loginForm = cn_system.login_4a_1(r, send_sms1, send_sms2, self.proxies, self.auth)
        #         # 返回值是tuple
        #         del self.order_list[_from_username][_order_name]
        #         return '4a_login_up', loginForm



    # 处理待办的命令
    # def deal_todo_order(self,_system, _from_username):
    #     # order_list 格式为 {fromusername:{ordername:{1:数值,2:数值……}}}
    #
    #     for _from_username in self.order_list.items():
    #         # _from_username格式为：（_from_username,{ordername:{1:数值,2:数值……})
    #
    #         for _order_name in _from_username[1].items():
    #             # _order_name 格式为：（ordername,{1:数值,2:数值……})
    #             if order_dic.get(_order_name[0]).get('system') == _system:
    #                 # ['operate_ok', _from_username, _order_name, order_param]
    #
    #                 return ['operate_ok', _from_username[0], _order_name[0], _order_name[1]]
    #
    #     return None


# def import_reload(a):
#     if a == "iot_system":
#         imp.reload(iot_system)
#     elif a == 'cn_system':
#         imp.reload(cn_system)


