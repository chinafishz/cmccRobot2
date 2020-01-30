import requests
from dic import ORDER_DIC
from libs.cmcc.main import CmccProcess



class MainProcess:
    def __init__(self):
        self.order_list = {}  # order_list表示待办理的命令
        self.chat_list = {}  # chart_list表示待回复的对话
        self.config_list = {}  # 同步一些配置和开关
        self.r = requests.session()

    def text_process(self, msg):
        from_username = msg.FromUserName
        text = msg.Text.strip().split(' ')
        while '' in text:
            text.remove('')

        order_name = text[0].lower()
        if order_name[0] != '#':
            return None  # 不是命令，所以不回复（None)
        elif ORDER_DIC.get(order_name) is None:
            return ['error', '%s不是可用的命令' % order_name]

        check_order_param_result = self.check_order_param(text)
        if check_order_param_result[0] == 'error':
            return check_order_param_result

    def check_order_param(self, text):
        order = text[0]
        param = text[1:]
        need_count = ORDER_DIC.get(order).get('param_count')
        if need_count != len(param):
            return ['error', '该命令需要输入%s个参数，但实际输入了%s个' % (need_count, len(param))]

        need_check_list = ORDER_DIC.get(order).get('need_check')
        property_check_result = {}
        for _param in param:
            property_check_result.update({_param: {}})
            for _item in need_check_list:
                if _item == 'type':
                    _result = None
                    if _param.isnumeric():
                        _result = int
                    elif _param[0] == '-' and _param[1:].isnumeric():
                        _result = int  # 当为负数时，isnumeric不去负号会报错
                    elif _param.islower() or _param.isupper():
                        _result = str
                    property_check_result[_param].update({'type': _result})
                elif _item == 'length':
                    property_check_result[_param].update({'length': len(_param)})
                elif _item == 'first_num':
                    property_check_result[_param].update({'first_num': _param[0]})

        result = {'order_name': order, 'param_count': need_count, 'system': ORDER_DIC.get(order).get('system'),
                  'actual_order': ORDER_DIC.get(order).get('actual_order')}
        for param_num in range(need_count):
            need_property = ORDER_DIC.get(order).get(param_num + 1).get('property')

            for _param, _dic in property_check_result.items():
                _is = True
                for _key, _value in need_property.items():
                    if _dic[_key] not in _value:
                        _is = False
                        continue
                if _is is True:
                    result.update({param_num: _param})
                    continue
            if _is is False:
                _list = []
                for _i in range(need_count):
                    _list.append(ORDER_DIC.get(order)[_i + 1]['name'] + ' ')
                return ['error', '参数%s有误,正确的格式为：%s %s' % (_param, order, ''.join(_list))]
        return ['success', result]

    def order_deal(self, raw_order):
        if raw_order['system'] in ['iot', '4a']:
            return CmccProcess.main_process(self.r, raw_order)
