# encoding:utf-8

"""
local WeChat channel
"""

import re
import websocket

from bridge.context import *
from bridge.reply import *
from channel.chat_channel import ChatChannel
from channel.wechat.wx_message import *
from common.singleton import singleton
from common.time_check import time_checker
from config import conf


def on_error(ws, error):
    logger.debug("[WX] on_error:{}".format(error))
    # WXChannel().startup()


def on_close(ws):
    logger.debug("[WX]on_close:{}".format(ws))


def on_open(ws):
    ws.send(get_personal_info())
    ws.send(get_user_list())
    logger.info("ws启动成功{}".format(get_now()))


def handle_notused_message(j):
    logger.debug("handle_notused_message:{}".format(j))


def handle_recv_txt_cite(j):
    logger.debug("handle_recv_txt_cite:{}".format(j))


def handle_recv_pic_msg(j):
    logger.debug("handle_recv_pic_msg:{}".format(j))


def on_message(ws, message):
    if "execption" == message:
        return
    j = json.loads(message)
    resp_type = j["type"]
    if resp_type != HEART_BEAT:
        logger.debug("on_message:{}".format(j))

    action = {
        HEART_BEAT: print,
        RECV_TXT_MSG: handle_recv_txt_msg,
        RECV_PIC_MSG: handle_recv_pic_msg,
        NEW_FRIEND_REQUEST: handle_notused_message,
        RECV_TXT_CITE_MSG: handle_recv_txt_cite,

        TXT_MSG: handle_notused_message,
        PIC_MSG: handle_notused_message,
        AT_MSG: handle_notused_message,

        USER_LIST: handle_wxuser_list,
        GET_USER_LIST_SUCCESS: handle_wxuser_list,
        GET_USER_LIST_FAIL: handle_wxuser_list,
        ATTACH_FILE: handle_notused_message,

        CHATROOM_MEMBER: handle_member_list,
        CHATROOM_MEMBER_NICK: handle_nick,
        DEBUG_SWITCH: handle_notused_message,
        PERSONAL_INFO: handle_personal_info,
        PERSONAL_DETAIL: handle_notused_message,
        OTHER_REQUEST: handle_other_msg
    }

    action.get(resp_type, handle_notused_message)(j)


def handle_wxuser_list(j):
    content = j["content"]
    i = 0
    for item in content:
        i += 1
        id = item["wxid"]
        name = item["name"]
        wxcode = item["wxcode"]
        user = conf().get_user_data(id)
        user["nick"] = name
        logger.debug("index:{},name:{},id:{},wxcode:{}".format(i, name, id, wxcode))

    conf().save_user_datas()


def handle_member_list(j):
    logger.debug("handle_member_list：" + j)


def handle_nick(j):
    """
    保存用户信息
    wxid:{
    nick:"",
    ${room_name}:${nick}
    }
    """
    data = json.loads(j["content"])
    wxid = str(data['wxid'])
    roomid = str(data['roomid'])
    nick = str(data['nick'])
    logger.debug("handle_nick:wxid:{},roomid:{},nick:{}".format(wxid, roomid, nick))
    if wxid != roomid:
        wxdata = conf().get_user_data(wxid)
        wxdata[roomid] =  nick

    conf().save_user_datas()
    logger.debug("handle_nick wx={}".format(wxdata))

def handle_personal_info(j):
    data = json.loads(j["content"])
    wxid = str(data['wx_id'])
    nick = str(data['wx_name'])
    WXChannel().name = nick
    WXChannel().user_id = wxid
    logger.debug("handle_personal_info name={}, user_id={}".format(WXChannel().name, WXChannel().user_id))


def handle_other_msg(j):
    pass


def handle_msg_user(wx_id, room_id, msg):
    is_room = msg.is_group
    wx_data = conf().get_user_data(wx_id)
    logger.debug("handle_msg_user wx_data={}".format(wx_data))
    if is_room:
        room_data = conf().get_user_data(room_id)
        msg.from_user_id = room_id
        msg.from_user_nickname = room_data.get("nick")

        msg.other_user_id = room_id
        msg.other_user_nickname = msg.from_user_nickname

        msg.actual_user_id = wx_id
        msg.actual_user_nickname = wx_data.get(room_id)
        logger.debug("handle_msg_user room_data={}".format(room_data))
    else:
        msg.from_user_id = wx_id
        msg.from_user_nickname = wx_data.get("nick")

        msg.other_user_id = wx_id
        msg.other_user_nickname = msg.from_user_nickname


def handle_recv_txt_msg(j):
    # ----------基础信息begin----------
    logger.debug("Current function name: {}".format(handle_recv_txt_msg.__name__))
    msg = WXMessage(j)
    wx_id = j["wxid"]
    room_id = ""
    content: str = j["content"].strip()
    is_room: bool
    if len(wx_id) < 9 or wx_id[-9] != "@":
        is_room = False
        wx_id: str = j["wxid"]
    else:
        is_room = True
        wx_id = j["id1"]
        room_id = j["wxid"]

    msg.is_group = is_room
    msg.content = content

    handle_msg_user(wx_id, room_id, msg)

    WXChannel().handle_msg(msg, is_room)


@singleton
class WXChannel(ChatChannel):
    NOT_SUPPORT_REPLYTYPE = [ReplyType.VOICE, ReplyType.IMAGE]

    def __init__(self):
        super().__init__()
        self.ws = None
        self.server = "ws://" + conf().get('wechat_local_host', "127.0.0.1:5555")
        logger.debug("WXChannel=" + self.server)

    def startup(self):
        # 是否调试模式
        websocket.enableTrace(False)
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.server, on_open=on_open, on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close)
        self.ws.run_forever(ping_interval=10)
        logger.debug("startup")

    @time_checker
    def handle_msg(self, cmsg: ChatMessage, isgroup: bool):
        logger.debug("handle_msg cmsg: {}, isgroup:{}".format(cmsg, isgroup))
        if isgroup:
            cmsg.to_user_id = self.user_id
            cmsg.to_user_nickname = self.name
        else:
            cmsg.to_user_id = self.user_id
            cmsg.to_user_nickname = self.name

        if isgroup:
            pattern = f'@{self.name}(\u2005|\u0020)'
            logger.debug("handle_msg pattern:{}".format(pattern))
            if re.search(pattern, cmsg.content):
                logger.debug(f'wx message {self.name} include at')
                cmsg.is_at = True

            self.find_nick(cmsg.actual_user_id, cmsg.from_user_id)

        if cmsg.ctype == ContextType.VOICE:
            if conf().get('speech_recognition') != True:
                return
            logger.debug("[WX]receive voice group: {}, msg: {}".format(isgroup, cmsg.content))
        elif cmsg.ctype == ContextType.IMAGE:
            logger.debug("[WX]receive image group: {}, msg: {}".format(isgroup, cmsg.content))
        else:
            logger.debug("[WX]receive text group: {} ,msg: {}".format(isgroup, cmsg))
        context = self._compose_context(cmsg.ctype, cmsg.content, isgroup=isgroup, msg=cmsg)
        if context:
            self.produce(context)

    def check_msg_data(self, msg):
        if msg.is_group and not msg.actual_user_nickname:
            msg.actual_user_nickname = conf().get_user_data(msg.actual_user_id).get(msg.from_user_id)

    def find_nick(self, wx_id, room_id):
        logger.debug("find_nick wxid:{},room_id:{}".format(wx_id, room_id))
        if wx_id is not None and room_id is not None:
            data = conf().get_user_data(wx_id)
            if data.get(room_id) is None:
                self.ws.send(get_chat_nick_p(wx_id, room_id))

    # 统一的发送函数，每个Channel自行实现，根据reply的type字段发送不同类型的消息
    def send(self, reply: Reply, context: Context):
        receiver = context["receiver"]
        if reply.type == ReplyType.TEXT or reply.type == ReplyType.ERROR or reply.type == ReplyType.INFO:
            self.ws.send(send_txt_msg(text_string=reply.content, wx_id=receiver))
            logger.info('[WX] sendMsg={}, receiver={}'.format(reply, receiver))
        else:
            logger.error('[WX] error sendMsg={}, receiver={}'.format(reply, receiver))

