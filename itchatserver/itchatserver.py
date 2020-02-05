import itchat
from itchat.content import TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO
import process
import json
import configparser
import logging
import time
import os

from libs.thrift_file.gen_py.test import Transmit
from libs.thrift_file.gen_py.test.ttypes import *
from libs.thrift_file.gen_py.test.constants import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import thrift


RELAY_USERNAME = {} # 格式： {姓名：{username: . output_type:输出类型, replay_list_type:转发来源类型, replay_list：转发给该用户的清单}
DATA_FILE_PATH = ''
SETTING_FILE_PATH = ''
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
THRIFTCLIENT= {'state': 'offline', 'last_connet_time': 0, 'isLoginin':False, 'error_count':0}  # 通过thrift 关联的参数


def load_contact(update=False):
    friends_list = itchat.get_friends(update)
    room_list = itchat.get_chatrooms(update)
    result = {}

    for _user in friends_list:
        _name = ''
        _pinyin = ''
        if _user.RemarkName != '':
            _name = _user.RemarkName
            try:
                _pinyin = _user.RemarkPYQuanPin
            except:
                pass
        else:
            _name = _user.NickName
            _pinyin = _user.PYQuanPin
        result.update({_user.UserName: {'type': 'f', 'name': _name, 'namepinyin': _pinyin}})

    for _room in room_list:
        _name = ''
        _pinyin = ''
        if _room.RemarkName != '':
            _name = _room.RemarkName
        else:
            _name = _room.NickName

        try:
            _pinyin = _room.PYQuanPin
        except:
            pass
        result.update({_room.UserName: {'type': 'r', 'name': _name, 'namepinyin': _pinyin}})

    global DATA_FILE_PATH
    with open(DATA_FILE_PATH + 'contactlist.json', 'w') as result_file:
        json.dump(result, result_file)


def search_contact(input, output_type, fuzzy_search=True):
    global DATA_FILE_PATH
    with open(DATA_FILE_PATH + 'contactlist.json', 'r') as result_file:
        contact_list = json.load(result_file)

    result_friend = {}
    result_room = {}
    for _user_name, _user_dic in contact_list.items():
        _search_result_name = _user_dic.get('name')
        _search_result_pinyin = _user_dic.get('namepinyin')
        if fuzzy_search == True:
            _search_result_name = _search_result_name.find(input)
            _search_result_pinyin = _search_result_pinyin.find(input)
        elif fuzzy_search == False:
            if _search_result_name != input and _search_result_pinyin != input:
                _search_result_name = -1
                _search_result_pinyin = -1
            else:
                pass

        if _search_result_name != -1 or _search_result_pinyin != -1:
            if _user_dic.get('type') == 'f':
                result_friend.update({_user_dic.get('name'): {'username': _user_name}})
            elif _user_dic.get('type') == 'r':
                result_room.update({_user_dic.get('name'): {'username': _user_name}})

    if output_type == 'only_group_UserName': # 仅输出群的的username
        result = []
        for _i in list(result_room.values()):
            result.append(_i['username'])
        return result
    else:
        return [result_friend, result_room]

def load_config_replay():
    global RELAY_USERNAME, SETTING_FILE_PATH
    config = configparser.ConfigParser()
    try:
        config.read(SETTING_FILE_PATH + 'config.ini')
    except:
        config.read('config.ini')
    section_path = dict(config.items('MsgReplay'))
    if section_path is None or section_path == '':
        return
    for i in section_path.get('list').split(','):
        _items = dict(config.items(i))
        RELAY_USERNAME.update({_items['replay_to']:{'username':search_contact(_items['replay_to'], output_type=_items['output_type'], fuzzy_search=False)[0], 'replay_list_type':_items['replay_list_type'], 'replay_list':_items['replay_list']}})


def login_success():
    load_contact()
    logger.info('已读取通信录')

    load_config_replay() # 读取信息转发设置
    logger.info('已读取信息转发设置')

    logger.info('login in')


def login_out():
    logger.info('login out')


def msg_relay(msg, relay_to):
    '''
    群：
        群名称：msg.User.NickName
        群成员有备注：msg.ActualNickName

    个人：
        有备注：msg.User.RemarkName
        没有备注：msg.User.NickName
    '''
    for key,value in relay_to.items():

        if value['replay_list_type'] == 'group':
            if msg.User.UserName[0:2] != '@@':
                return

            group_name = ''
            user_name = ''
            try:
                group_name = msg.User.NickName
            except:
                pass

            if group_name in value['replay_list']:
                global DATA_FILE_PATH
                user_name = msg.ActualNickName

                if msg.type == TEXT:
                    itchat.send('[%s]%s: \n%s' % (group_name, user_name, msg.text), toUserName=value['username'])
                elif msg.type == PICTURE:
                    temp_path = DATA_FILE_PATH + 'temp/' + msg.fileName
                    msg.download(temp_path)
                    itchat.send('[%s]%s:' % (group_name, user_name), toUserName=value['username'])
                    itchat.send_image(temp_path, toUserName=value['username'])
                    os.remove(temp_path)
                elif msg.type in [ATTACHMENT, RECORDING]:
                    temp_path = DATA_FILE_PATH + 'temp/' + msg.fileName
                    msg.download(temp_path)
                    itchat.send('[%s]%s:' % (group_name, user_name), toUserName=value['username'])
                    itchat.send_file(temp_path, toUserName=value['username'])
                    os.remove(temp_path)
                elif msg.type == VIDEO:
                    temp_path = DATA_FILE_PATH + 'temp/' + msg.fileName
                    msg.download(temp_path)
                    itchat.send('[%s]%s:' % (group_name, user_name), toUserName=value['username'])
                    itchat.send_video(temp_path, toUserName=value['username'])
                    os.remove(temp_path)


        elif value['replay_list_type'] == 'friend':
            if msg.User.UserName[0:2] == '@@':
                return

            # TODO :之后补充


def sendto_LAN_client(msg):
    '''
    作用：发给局域网内的客户端，通过thrift调用
    :param msg: itchat的msg参数
    :return: 没有返回
    '''
    if THRIFTCLIENT['state'] == 'online':
        try:
            result = THRIFTCLIENT['object'].sayMsg(msg.text)
        except thrift.transport.TTransport.TTransportException as e:
            logger.warning('[失败]sendto_LAN_client:' + str(e))
            THRIFTCLIENT.update({'state': 'offline'})
        pass
    elif THRIFTCLIENT['state'] == 'offline' and THRIFTCLIENT['isLoginin'] is True :
        last_connet_time = THRIFTCLIENT['last_connet_time']
        if time.time() - last_connet_time > 40:
            THRIFTCLIENT.update({'last_connet_time': time.time()})
            result = thrift_init()
            if result == 'error':
                old_count = THRIFTCLIENT.get('error_count')
                THRIFTCLIENT.update({'error_count': old_count + 1})
                if old_count + 1 >= 10:
                    THRIFTCLIENT.update({'state': 'offline', 'isLoginin':False})
                    logger.info('局域网客户端状态更新为下线')
            elif result == 'success':
                THRIFTCLIENT.update({'state': 'online', 'isLoginin':True, 'error_count':0})
                logger.info('局域网客户端状态更新为上线')


def order_process(msg):
    process_mainprocess = process.MainProcess()
    response = process_mainprocess.text_process(msg)

    if response is None:
        return
    elif type(response) is list:
        if response[0] == 'error':
            return response[1]
        elif response[0] == 'success':
            deal_result = process_mainprocess.order_deal(response[1])
            if deal_result[0] in ['success', 'error']:
                if type(deal_result[1]) is tuple:
                    for i in deal_result[1]:
                        itchat.send(i, toUserName=msg.UserName)
                else:
                    return deal_result[1]
            elif deal_result[0] == 'warning':
                itchat.send(deal_result[2])
                return deal_result[1]
        elif response[0] == 'warning':
            itchat.send(response[2])
            return response[1]


@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True)
def msg_receive_text(msg):
    global RELAY_USERNAME, THRIFTCLIENT
    sendto_LAN_client(msg) # 发给局域网内的客户端，通过thrift调用
    msg_relay(msg, relay_to=RELAY_USERNAME)
    order_result = order_process(msg) # 命令处理
    return order_result


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True, isGroupChat=True)
def img_receive(msg):
    msg_relay(msg, relay_to=RELAY_USERNAME)
    img_binary  =msg.text()




def load_config_file():
    config = configparser.ConfigParser()
    config.read('config.ini')
    section_path = dict(config.items('path'))

    global DATA_FILE_PATH, SETTING_FILE_PATH
    DATA_FILE_PATH = section_path.get('data_file')
    SETTING_FILE_PATH = section_path.get('setting_file')

    # 如果无法读取到默认的数据的目录，改为当前目录的的data/,目的为避免data文件内容上传到github
    try:
        config.read(SETTING_FILE_PATH + 'config.ini')
    except Exception as e:
        DATA_FILE_PATH = 'data/'
        SETTING_FILE_PATH = ''

    logger.info('配置初始化完成')


def thrift_init():
    '''
    用途：初始化到局域网客户端的thrift配置
    :return: 
    '''
    config = configparser.ConfigParser()
    config.read('config.ini')
    section_path = dict(config.items('SendTo_THRIFTCLIENT_byThrift'))
    transport = TSocket.TSocket(section_path.get('ip'), section_path.get('port'))
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    global THRIFTCLIENT
    client = Transmit.Client(protocol)
    THRIFTCLIENT.update({'object':client})
    try:
        transport.open()
        THRIFTCLIENT.update({'state':'online'})
        logger.info('thrift服务初始化完成')
        return 'success'
    except thrift.transport.TTransport.TTransportException as e:
        logger.warning(e)
        return 'error'
    except thrift.transport.TSocket as e:
        logger.warning(e)

def start():
    load_config_file()
    thrift_init()

    itchat.auto_login(hotReload=True, enableCmdQR=False, loginCallback=login_success, exitCallback=login_out)
    itchat.run()


if __name__ == "__main__":
    start()
