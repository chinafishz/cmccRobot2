import itchat
from itchat.content import TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO
from process import MainProcess
import json
import configparser

RELAY_USERNAME = {} # 格式： {姓名：{username: . output_type:输出类型, replay_list_type:转发来源类型, replay_list：转发给该用户的清单}
DATA_FILE_PATH = ''
SETTING_FILE_PATH = ''


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


def getfriend_fromcontact(input, output_type, fuzzy_search=True):
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
        else:
            if _search_result_name != input and _search_result_pinyin != input:
                _search_result_name = -1
                _search_result_pinyin = -1
            else:
                pass
        if _search_result_name != -1 or _search_result_pinyin != -1:
            if _user_dic.get('type') == 'f':
                result_friend.update({_user_dic.get('name'): {'username': _user_name}})
            elif _user_dic.get('type') == 'r' and output_type not in ['friend_UsreName']:
                result_room.update({_user_dic.get('name'): {'username': _user_name}})

    if output_type == 'friend_UsreName':
        result = []
        for _i in list(result_friend.values()):
            result.append(_i['username'])
        return result
    else:
        return [result_friend, result_room]

def load_config_replay():
    global RELAY_USERNAME, SETTING_FILE_PATH
    config = configparser.ConfigParser()

    try:
        config.read(SETTING_FILE_PATH + 'config.ini', encoding='utf-8')
    except:
        config.read('config.ini', encoding='utf-8')
    section_path = dict(config.items('msg_replay'))
    if section_path is None:
        return
    for i in section_path.get('list').split(','):
        _items = dict(config.items(i))
        RELAY_USERNAME.update({_items['replay_to']:{'username':getfriend_fromcontact(_items['replay_to'], output_type=_items['output_type'], fuzzy_search=False)[0], 'replay_list_type':_items['replay_list_type'], 'replay_list':_items['replay_list']}})


def login_success():
    load_contact()
    load_config_replay() # 读取信息转发设置
    print('login in')


def login_out():
    print('login out')


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
                user_name = msg.ActualNickName

                if msg.type == TEXT:
                    itchat.send('[%s]%s: \n%s' % (group_name, user_name, msg.text), toUserName=value['username'])
                '''
                elif _type == PICTURE:
                    itchat.send('[' + _group_name + ']' + _user_name + ':', toUserName=kivy.laopo_username)
                    itchat.send_image(_path, toUserName=kivy.laopo_username)
                elif _type in [ATTACHMENT, RECORDING]:
                    itchat.send('[' + _group_name + ']' + _user_name + ':', toUserName=kivy.laopo_username)
                    itchat.send_file(_path, toUserName=kivy.laopo_username)
                elif _type in [VIDEO]:
                    itchat.send('[' + _group_name + ']' + _user_name + ':', toUserName=kivy.laopo_username)
                    itchat.send_video(_path, toUserName=kivy.laopo_username)
                '''

        elif value['replay_list_type'] == 'friend':
            if msg.User.UserName[0:2] == '@@':
                return

            # TODO :之后补充


@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True)
def msg_receive_text(msg):
    global RELAY_USERNAME
    msg_relay(msg, relay_to=RELAY_USERNAME)
    response = MainProcess.text_process(msg)
    if response is None:
        return
    elif type(response) is list:
        if response[0] == 'error':
            return response[1]
        elif response[0] == 'success':
            deal_result = MainProcess.order_deal(response[1])
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


def load_config_file():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    section_path = dict(config.items('path'))

    global DATA_FILE_PATH, SETTING_FILE_PATH
    DATA_FILE_PATH = section_path.get('data_file')
    SETTING_FILE_PATH = section_path.get('setting_file')


def start():
    load_config_file()
    itchat.auto_login(hotReload=True, enableCmdQR=False, loginCallback=login_success, exitCallback=login_out)
    itchat.run()


if __name__ == "__main__":
    start()
