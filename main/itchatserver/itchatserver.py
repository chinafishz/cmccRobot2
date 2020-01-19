import itchat
from itchat.content import TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO
from mainprocess import MainProcess
import json


WIFE_USERNAME = ''

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
        result.update({_user.UserName: {'type':'f', 'name': _name, 'namepinyin': _pinyin}})

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
        result.update({_room.UserName:{'type':'r', 'name':_name, 'namepinyin':_pinyin}})

    with open('contactlist.json', 'w') as result_file:
        json.dump(result, result_file)


def getfriend_fromcontact(input, output_type, fuzzy_search=True):
    with open('contactlist.json', 'r') as result_file:
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
                    result_friend.update({_user_dic.get('name'): {'username':_user_name}})
            elif _user_dic.get('type') == 'r' and output_type not in ['friend_UsreName']:
                result_room.update({_user_dic.get('name'): {'username':_user_name}})

    if output_type == 'friend_UsreName':
        result = []
        for _i in list(result_friend.values()):
            result.append(_i['username'])
        return result
    else:
        return [result_friend, result_room]


def login_success():
    load_contact()
    WIFE_USERNAME = getfriend_fromcontact('老婆', output_type='friend_UsreName', fuzzy_search=False)[0]
    print('login in')


def login_out():
    print('login out')


def to_wife(msg):
    if msg.User.UserName[0:2] != '@@':
        return

    '''
    群：
        群名称：msg.User.NickName
        群成员有备注：msg.ActualNickName
        
   个人：
        有备注：msg.User.RemarkName
        没有备注：msg.User.NickName
    '''
    group_name = ''
    user_name = ''
    try:
        group_name = msg.User.NickName
    except:
        pass

    if group_name in ['测试群']:
        user_name = msg.ActualNickName

    if msg.type == TEXT:
        itchat.send('[%s]%s: \n%s' % (group_name, user_name, msg.text), toUserName=WIFE_USERNAME)
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

@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True)
def msg_receive_text(msg):
    to_wife(msg)
    response = MainProcess.text_process(msg)
    if response is None:
        return
    elif type(response) is list:
        if response[0] == 'error':
            return response[1]
        elif response[0] == 'sucess':
            deal_result = MainProcess.order_deal(response[1])
        elif response[0] == 'warning':
            itchat.send(response[2])
            return response[1]
            
def start():
    itchat.auto_login(hotReload=True, enableCmdQR=False, loginCallback=login_success, exitCallback=login_out)
    itchat.run()


if __name__ == "__main__":
    start()