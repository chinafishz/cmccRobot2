import cn_system
from dic import order_dic
import iot_system
from bs4 import BeautifulSoup
import importlib as imp
import requests


send_sms1 = '41608446240A6782F2A0F031426EDC066CF24674F3F0586A4D5FF056D75FF4AB'
send_sms2 = '41608446240A6782F2A0F031426EDC066CF24674F3F0586AF1E3983438A092966F9B57FEF7B22FB7D01E1BDF5B4421CB6069ED5C9B03B580'
cn_pwd_saw = 'QWer!@34'


def process_a05(_split):
    # 获取输入的参数对比命令要求后参数的结果
    # self = _split :list

    order_name = _split[0].lower()
    # _split 为用户的属于，可能会出现大写英文字母

    _order_dic_result = order_dic[order_name]
    # _order_dic_result = {'id': 1001,'param_count': 1,1: {'name': 'phoneNum','property': {'type': int,
    #                      'length': [13,11], 'first_num': '1'}}
    # 常用数据

    if order_name[0] == '#':
        _split = _split[1:]
    if len(_split) != 0:
        # Todo:a06

        _param_count = _order_dic_result['param_count']
        if len(_split) > _param_count:
            return 'error401', _param_count, len(_split)
        else:
            _property_kinds = {}
            _i = 0
            while _i < _param_count:
                _i = _i + 1
                _property_kinds.update(_order_dic_result[_i].get('property'))
                # 将所有属性放在一个字典里面，每个参数都LOAD一次这个属性，即使用不着

            _result_a06 = process_a06(_split, _property_kinds)
            # 返回每个输入的参数的属性值

            _result_a08 = process_a08(_result_a06, _order_dic_result)
            # 返回输入参数与命令要求的参数的对比结果
            # 格式为字典：{1:0,2:1,……,N:M第N个命令函数的值是对应第M个输入函数}

            if _result_a08 != {}:
                _result_param_available = {}
                for _i in _result_a08.items():
                    _result_param_available.update({_i[0]: _split[_i[1]]})
                return _result_param_available

    else:
        # Todo:a07
        print('todo07')
        pass


def process_a06(_text_split, param_property_kinds):
    result = {}
    # result为输入的参数对应的类型的查询结果

    _i = -1
    for _param in _text_split:
        _i = _i + 1
        result.update({_i: {}})
        # 第一个输入参数起始序号为0

        for _property_name in param_property_kinds:
            if _property_name == 'type':
                if _param.isnumeric():
                    result[_i].update({_property_name: int})
                elif _param[0] == '-' and _param[1:].isnumeric():
                    # 当为负数时，isnumeric不去负号会报错

                    result[_i].update({_property_name: int})
                elif _param.islower() or _param.isupper():
                    result[_i].update({_property_name: str})

                else:
                    result[_i].update({_property_name: ''})
            elif _property_name == 'length':
                result[_i].update({_property_name: len(_param)})
            elif _property_name == 'first_num':
                result[_i].update({_property_name: _param[0]})

    return result


def process_a08(_input_property, _order_require):

    match_result = {}
    # 代表命令要求的参数是否已经知道了匹配的输入参数，''代表没找到，数字代表找到

    _i = 0
    while _i < _order_require['param_count']:
        # 思路：目前采用忽略多余的输入参数，即假如输入参数不匹配，不报错，只保存匹配的参数
        #     并在之后的步骤a0X找到那些命令参数还没有数值。
        _i = _i + 1
        _param_id = _order_require[_i]
        # _param_id 命令要求的参数字典
        # 格式例子：
        # {
        #     'name': 'phoneNum',
        #     'property': {'type': int, 'length': [13, 11], 'first_num': '1'},
        # }

        for _j in _input_property:
            # _j 为输入参数的id

            _input = _input_property[_j]
            # 输入的参数属性种类明细
            # 格式为：{'type': int, 'length':13, 'first_num': '1'}

            if _input == {}:
                continue
            _param_id_property = _param_id['property']
            # _param_id_property 命令要求的属性明细
            # 格式为：{'type': int, 'length':[11,13], 'first_num': '1'}

            _is_match = 1
            # 代表匹配结果，0代表没找到，1代表找到

            for _k in _param_id_property.items():
                # _k格式为：('type',int)  ('length',[11,13])

                if type(_k[1]) == list:
                    if _input.get(_k[0]) not in _k[1]:
                        _is_match = 0
                else:
                    if _k[1] != _input.get(_k[0]):
                        _is_match = 0

            # 如果循环结束后_is_match还是1,证明地_j个输入参数符合第_i个命令参数的全部要求

            if _is_match == 1:
                del _input_property[_j]
                match_result.update({_i: _j})
                break
    return match_result


class CnMsgProcess:
    def __init__(self):
        self.order_list = {}
        # order_list表示待办理的命令
        
        self.chat_list = {}
        # chart_list表示待回复的对话
        
        self.config_list = {}
        # 同步一些配置和开关
        
        self.r = requests.session()
        self.proxy_load = cn_system.proxy_load()


    def cn_msg_process(self, msg):
        _from_username = msg.FromUserName
        _text = msg.Text.strip()
        _split = _text.split(' ')
        # 分列后[命令,参数……] :list
        # 先判断是否为字典内的命令

        while '' in _split:
            _split.remove('')

        _order_name = _split[0].lower()
        if self.chat_list.get(_from_username) is None:
            # 先判断是否在chat_list

            if _text[0] != '#':
                return None
                # 不是命令，所以不回复（None)

            else:
                # Todo:a01

                if order_dic.get(_order_name) is not None:
                    # 判定为有效的命令，才从这里真正处理指令`
                    # Todo:a05

                    pass
                    # 多个分支汇总到a05

                else:
                    return ['error', '%s不是可用的命令' % _order_name]
        else:
            if _text[0] == '#' and self.chat_list[_from_username].get(_text[0]) is None:
                # Todo:a01

                if order_dic.get(_order_name) is not None:
                    # Todo:a05

                    pass
                    # 多个分支汇总到a05

                else:
                    return ['error', '不是可用的命令']

            else:
                # Todo:a03
                # 日后再补充
                return None

        # a05:

        _result_process_a05 = process_a05(_split)
        # 获取输入的参数对比命令要求后参数的结果
        # 格式为： {1:'abc',3:'cde'……}
        # 如果是错误信息，返回类型为tuple

        if _result_process_a05 is None:
            return ['error', '%s的参数不正确' % _order_name]
        elif type(_result_process_a05) == tuple:
            if _result_process_a05[0] == 'error401':
                return ['error', '该命令需要输入%s个参数，但实际输入了%s个' % (_result_process_a05[1], _result_process_a05[2])]
            # elif:
        # else:

        _param_operation_dic = {}
        # _param_operation_dic 为合并到chat_dic或order_dic前的过渡字典

        for _i in range(order_dic.get(_order_name)['param_count']):
            #  _i 是从0开始，而_result_process_a05的格式为：{1: '12345678901'}
            # 所以需要_i+1

            if _result_process_a05.get(_i + 1) is not None:
                # 仅在参数输入有效的情况下生效，其他情况返回的是文字错误

                _param_operation_dic.update({_i + 1: _result_process_a05.get(_i + 1)})
                # 格式为：{1:'ABC',3:...} 2没数值，所以留空

                self.chat_list.setdefault(_from_username, {}).setdefault(_order_name, {}).update(_param_operation_dic)
                # 将本次输入的参数合并到对话列表中，如果有新增则补充，重复也覆盖，没涉及到的则不影响
                # 格式为：{fromusernane:{order name:{1:'ABC',3•••}}}

            else:
                pass
        order_param = self.chat_list.get(_from_username).get(_order_name)
        if len(order_param) == order_dic.get(_order_name)['param_count']:
            return ['operate_ok', _from_username, _order_name, order_param]
            # 返回结果给cmcc操作

        else:
            _result = '错误（缺参数），命令格式为： %s ' % _order_name
            for _i in range(order_dic.get(_order_name)['param_count']):
                if self.chat_list.get(_from_username).get(_order_name).get(_i + 1) is None:
                    _result = _result + ' ' + order_dic.get(_order_name).get(_i + 1).get('name')
                else:
                    _result = _result + ' ' + self.chat_list.get(_from_username).get(_order_name).get(_i + 1)
            return ['error', _result]

    def cmcc_process(self, _response):
        # _response 格式为 ['operate_ok', _from_username, _order_name, order_param] 或 none 或 文字

        if _response is None:
            return None
        elif _response[0] == 'error':
            return 'error', _response[1]
        elif type(_response) is list and _response[0] == 'operate_ok':
            self.chat_to_order(_response)
            _order_name = _response[2]

            # _order_param:命令参数
            _order_param = _response[3]
            _from_username = _response[1]
            _cmcc_system_name = order_dic.get(_order_name).get('system')
            _actual_order = order_dic.get(_order_name).get('actual_order')
            _proxies = self.proxy_load[0]
            _auth = self.proxy_load[1]
            _r = self.r
            _order_list = self.order_list
            _chat_list = self.chat_list
            _config_list = self.config_list

        if _cmcc_system_name == 'iot':
            # 初始化时已经把r导入，之后的函数就不用再考虑输入r了

            if _config_list.setdefault('iot_loginning', 0) == 1:
                return 'hurry','有新的指令，但iot系统仍没登陆'
            if iot_system.test_alive(_r, _proxies, _auth) != 'alive':
                # 4a login
                loginForm = cn_system.login_4a_1(_r, send_sms1, send_sms2, _proxies, _auth)
                # 返回值是tuple
                self.config_list['iot_loginning'] = 1
                # 其他同类命令则不再操作登陆系统

                return '4a_login_up', loginForm

            # 如果系统没登出，则继续处理指令

            if _actual_order == '#iot_puk':
                try:
                    # 要求返回公司名称
                    _entityName =iot_system.iot_phone_query_base(_r, _order_param.get(1), _proxies, _auth, 'name')
                    _result = iot_system.iot_puk(_r, _proxies, _auth)
                except:
                    return 'error', _order_param.get(1) + '的puk查询失败，没有查询结果，请检查输入的号码'
                else:
                    # 判断是否为白名单公司
                    if _entityName in order_dic['#puk']['whitelist']:
                        return 'success', _order_param.get(1) + 'puk为：' + _result
                    else:
                        return 'Warning', _order_param.get(1) + 'puk为：' + _result, _order_param.get(1) + '公司名称为：' + _entityName

                finally:
                    del self.order_list[_from_username][_order_name]

            elif _actual_order == '#iot_status':
                # _result = iot_system.iot_status(_r, _order_param.get(1), _proxies, _auth)
                # del self.order_list[_from_username][_order_name]
                try:
                    _result = iot_system.iot_status(_r, _order_param.get(1), _proxies, _auth)
                except:
                    return 'error', _order_param.get(1) + '的状态查询失败，没有查询结果，请检查输入的号码'
                else:
                    return 'success', _order_param.get(1) + '状态为：' + _result
                finally:
                    del self.order_list[_from_username][_order_name]

            elif _actual_order == '#iot_outstanding_fees':
                try:
                    _result_step_1 = iot_system.iot_outstanding_fees_1(_r, _order_param.get(1), _proxies, _auth)
                    _result = iot_system.iot_outstanding_fees_2(_r, _result_step_1, _order_param.get(1), _proxies, _auth)
                except:
                    return 'error', _order_param.get(1) + '的余额查询失败，没有查询结果，请检查输入的号码'
                else:
                    return 'success', _order_param.get(1) + '的余额为：' + _result
                finally:
                    del self.order_list[_from_username][_order_name]

            elif _actual_order == '#laina500':
                _result = iot_system.iot_laina500(_r, _order_param.get(1), _proxies, _auth)
                del self.order_list[_from_username][_order_name]
                if _result == '办理完成':
                    return 'success', _order_param.get(1) + '已经开机,但暂采用人工加流量池方式，稍后加入再回复,请谅解'
                else:
                    return 'error',_result

            # 申请开机
            elif _actual_order == '#open&stop_shenqing':
                try:
                    _dic = {'': ['深**徕纳智能科技有限公司'], '@146bc331344a6eedc213bed5b29fa465e26a6673b52b566f74e45fb2adf6dd9d':['all']}
                    # 配置微信群能操作那个公司的号码的权限

                    _dic_param = _dic.get(_from_username)
                    result =''
                    if _dic_param is not None:
                        _result = iot_system.iot_phone_query_base_setp1(_r, _order_param.get(1), _proxies, _auth, 'name')
                        s2 = _result[0]
                        _name = _result[1]
                        if _name in _dic_param or _dic_param == ['all']:
                            iot_system.iot_phone_query_base_setp2(_r, s2, _order_param.get(1), _proxies, _auth)
                            result = iot_system.stop_and_open(_r,'申请开机', _order_param.get(1), _proxies, _auth)
                        else:
                            return 'error', + _order_param.get(1) + '号码所属公司与本微信群配置不一致'
                    else:
                        return 'error', '没配置' + _order_param.get(1) + '号码归属公司的开机权限'
                except:
                    return 'error', _order_param.get(1) + '申请开机操作【失败】,请查核原因'
                else:
                    return 'success', _order_param.get(1) + '申请开机' + result
                finally:
                    del self.order_list[_from_username][_order_name]

        # ===========ESOP系统===========
        elif _cmcc_system_name == 'ESOP':
            pass

        elif _cmcc_system_name == '4a':
            if _actual_order == '#4a_sms':
                _result = cn_system.login_4a_2(_r, cn_pwd_saw, _order_param.get(1), _order_param.get(2), _proxies,
                                               _auth)
                # login_4a_2(r, cn_pwd_saw, sms_pwd, loginForm2, _proxies, _auth)
                # 返回值是tuple 或者 none
                if _result is None:
                    return 'error', '登陆失败'
                del self.order_list[_from_username][_order_name]
                return '4a_login_up_success', _result
                # 直接返回结果，由main处理

            elif _actual_order == '#4a_iot':
                s = cn_system.iot_login(_r, _order_param.get(1), _proxies, _auth)
                # iot_login(r, _system_name_id, _proxies, _auth)

                if self.config_list.setdefault('iot_loginning',0) == 1:
                    self.config_list['iot_loginning'] = 0
                del self.order_list[_from_username][_order_name]
                return 'iot_login_up', 1
            elif _actual_order == '#4a_login_clone':
                loginForm = cn_system.login_4a_1(_r, send_sms1, send_sms2, _proxies, _auth)
                # 返回值是tuple
                del self.order_list[_from_username][_order_name]
                return '4a_login_up', loginForm

    # 将对话的结果转到命令字典
    def chat_to_order(self, _response,):
        # _response 格式为 ['operate_ok', _from_username, _order_name, order_param]

        if _response[0] != 'operate_ok':
            return
        _from_username = _response[1]
        _order_name = _response[2]
        _order_param = _response[3]
        if self.order_list.get(_from_username) is not None:
            self.order_list[_from_username][_order_name] = _order_param
        else:
            self.order_list.setdefault(_from_username,{_order_name:_order_param})
        if self.chat_list[_from_username].get(_order_name) is not None:
            del self.chat_list[_from_username][_order_name]

    # 处理待办的命令
    def deal_todo_order(self,_system, _from_username):
        # order_list 格式为 {fromusername:{ordername:{1:数值,2:数值……}}}

        for _from_username in self.order_list.items():
            # _from_username格式为：（_from_username,{ordername:{1:数值,2:数值……})

            for _order_name in _from_username[1].items():
                # _order_name 格式为：（ordername,{1:数值,2:数值……})
                if order_dic.get(_order_name[0]).get('system') == _system:
                    # ['operate_ok', _from_username, _order_name, order_param]

                    return ['operate_ok', _from_username[0], _order_name[0], _order_name[1]]

        return None


class CnMsgProcess_kivy(CnMsgProcess):
    def __init__(self, cn_order_list, cn_chat_list, cn_config_list, r, _kivy, cn_weixin_chat):
        self.order_list = cn_order_list
        self.chat_list = cn_chat_list
        self.config_list = cn_config_list
        self.r = r
        self.proxy_load = cn_system.proxy_load()
        self.kivy = _kivy
        self.kivy_text_all = ''
        self.weixin_chat = cn_weixin_chat


def import_reload(a):
    if a == "iot_system":
        imp.reload(iot_system)
    elif a == 'cn_system':
        imp.reload(cn_system)


