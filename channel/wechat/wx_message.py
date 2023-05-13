import datetime
import json
import time
from bridge.context import ContextType
from channel.chat_message import ChatMessage
from common.tmp_dir import TmpDir
from common.log import logger

# Signal Number
HEART_BEAT = 5005
RECV_TXT_MSG = 1
RECV_PIC_MSG = 3
NEW_FRIEND_REQUEST = 37
RECV_TXT_CITE_MSG = 49

TXT_MSG = 555
PIC_MSG = 500
AT_MSG = 550

USER_LIST = 5000
GET_USER_LIST_SUCCESS = 5001
GET_USER_LIST_FAIL = 5002
ATTACH_FILE = 5003
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020

DEBUG_SWITCH = 6000
PERSONAL_INFO = 6500
PERSONAL_DETAIL = 6550

DESTROY_ALL = 9999
OTHER_REQUEST = 10000


def get_id():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id


def get_chatroom_memberlist(wx_id, room_id):
    """
    获取群成员列表
    :return:
    """
    qs = {
        "id": get_id(),
        "type": CHATROOM_MEMBER,
        "wxid": wx_id,
        "roomid": room_id,
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def get_chat_nick_p(wx_id, room_id):
    """
    获取群成员昵称
    :param wx_id: 微信ID
    :param room_id: 房间ID
    :return:
    """
    qs = {
        "id": get_id(),
        "type": CHATROOM_MEMBER_NICK,
        "wxid": wx_id,
        "roomid": room_id,
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def get_personal_info():
    """
    获取本号码信息
    :return:
    """
    qs = {
        "id": get_id(),
        "type": PERSONAL_INFO,
        "wxid": "ROOT",
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def get_personal_detail(wx_id):
    """
    获取本号码详情
    :param wx_id:
    :return:
    """
    qs = {
        "id": get_id(),
        "type": PERSONAL_DETAIL,
        "wxid": wx_id,
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def get_user_list():
    """
    获取微信通讯录用户名字和wxid
    获取微信通讯录好友列表
    """
    qs = {
        "id": get_id(),
        "type": USER_LIST,
        "content": "user list",
        "wxid": "null",
    }
    return json.dumps(qs)


def send_txt_msg(text_string, wx_id):
    """
    发送文本消息
    :param text_string: 文本内容
    :param wx_id: 微信ID
    :return:
    """
    qs = {
        "id": get_id(),
        "type": TXT_MSG,
        "wxid": wx_id,
        "roomid": "",
        "content": text_string,  # 文本消息内容
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_at_meg(wx_id, room_id, content, nickname):
    """
    发送图片消息
    :param wx_id:
    :param room_id:
    :param content:
    :param nickname:
    :return:
    """
    qs = {
        "id": get_id(),
        "type": AT_MSG,
        "wxid": wx_id,
        "roomid": room_id,
        "content": content,
        "nickname": nickname,
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_pic_msg(wx_id, content):
    """
    发送图片消息
    :param wx_id:
    :param content:
    :return:
    """
    qs = {
        "id": get_id(),
        "type": PIC_MSG,
        "wxid": wx_id,
        "roomid": "",
        "content": content,
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_wxuser_list():
    """
    发送用户列表
    :return:
    """
    qs = {
        "id": get_id(),
        "type": USER_LIST,
        "wxid": "",
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s

def get_now():
    now = datetime.datetime.now()
    dt_string = "[" + now.strftime("%Y-%m-%d %H:%M:%S") + "]"
    return dt_string

class WXMessage(ChatMessage):

    def __init__(self, msg):
        super().__init__(msg)
        self.msg_id = msg['id']
        self.create_time = msg['time']
        self.ctype = ContextType.TEXT
        self.content = msg['content']

