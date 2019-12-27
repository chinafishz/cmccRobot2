import requests
from dic import ORDER_DIC

class MainProcess:
    def __init__(self):
        self.order_list = {}    # order_list表示待办理的命令
        self.chat_list = {}    # chart_list表示待回复的对话
        self.config_list = {}    # 同步一些配置和开关
        self.r = requests.session()
       # self.proxy = cmcc_system.proxy_load()

    def text_process(msg):
        from_username = msg.FromUserName
        text = msg.Text.strip().split(' ')
        while '' in text:
            text.remove('')
         
         order_name = text[0].lower()
        if order_name[0] != '#':
            return  None  # 不是命令，所以不回复（None)
        elif ORDER_DIC.get(order_name) is None:
            return ['error', '%s不是可用的命令' % order_name]
        
    