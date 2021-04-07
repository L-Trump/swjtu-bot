import re
import typing as T
from graia.application import (
    GraiaMiraiApplication, GroupMessage,
    FriendMessage,
    MessageChain, Source, Member, Friend
)
from graia.application.logger import LoggingLogger
from graia.application.message.elements.internal import Plain, Quote
from graia.broadcast import Broadcast

from .._utils import Sender, Type, reply, common
from .._utils.database import Database
from .._utils.env import env

logger = LoggingLogger
config = Database.load(common.getRunningPath(False) / 'config' / 'customReply.json')

sub_app: GraiaMiraiApplication = env['app']
bcc: Broadcast = env['bcc']

method_alias = {
    'equal': '完全相等',
    'startwith': '匹配开头',
    'endwith': '匹配结尾',
    're': '正则匹配',
    'contain': '包含文本'
}


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


class Command:
    @classmethod
    def add(cls, rule, qq: int = None, group: int = None, glb: bool = False):
        item: str = ""
        if glb:
            item = 'global'
        elif qq:
            item = f'qq{qq}'
        elif group:
            item = f'group{group}'
        if not config.get(item): setattr(config, item, [])
        if 'reply' in rule and rule not in config.get(item):
            config.get(item).append(rule)
            config.save()

    @classmethod
    def parseCommand(cls, text: str, qq: int = None, group: int = None):
        obj = re.match(
            r'\s*[。.]reply\s*?(qq|group|global)?\s*?(\d+)?\s*?(contain|startwith|endwith|equal|re)\s*([\S\s]+?)\n\s*([\S\s]+)',
            text)
        if not obj: return False
        tp, num, mode, cmd, reply = obj.groups()
        glb = False
        if not all([mode, cmd, reply]): return False
        if tp:
            if tp == 'qq' and num:
                qq = int(num)
                group = None
            elif tp == 'group' and num:
                group = int(num)
                qq = None
            elif tp == 'global':
                glb = True
                qq = None
                group = None
            else:
                return False

        if not any([qq, group, glb]): return False
        rule = {
            mode: cmd,
            'reply': reply
        }
        cls.add(rule=rule, qq=qq, group=group, glb=glb)
        return f'成功为{"QQ" if qq else "群" if group else "全局"}{qq if qq else group if group else ""}添加自动回复\n模式: {method_alias.get(mode, mode)}\n内容: {cmd}\n回复: {reply} '

    @classmethod
    def parse(cls, text: str, sender: "Sender", event_type: "Type"):
        item = f"{'qq' if event_type == 'FriendMessage' else 'group'}{sender.id if event_type == 'FriendMessage' else sender.group.id}"
        rules = config.get('global', []) + config.get(item, [])
        if not rules:
            return None
        data = {
            'type': '好友' if event_type == 'FriendMessage' else '群',
            'qq': sender.id,
            'qqname': sender.name if event_type == 'GroupMessage' else sender.nickname,
            'group': sender.group.id if event_type == 'GroupMessage' else None,
            'groupname': sender.group.name if event_type == 'GroupMessage' else None,
            'text': text
        }
        for rule in rules[-1::-1]:
            regex = None
            if rule.get('disable', False): continue
            if 'reply' not in rule: continue
            if rule.get('contain') and text.find(rule['contain']) == -1: continue
            if rule.get('equal') and text != rule['equal']: continue
            if rule.get('startwith') and not text.startswith(rule['startwith']): continue
            if rule.get('endwith') and not text.endswith(rule['endwith']): continue
            if rule.get('re'):
                obj = re.match(rule['re'], text)
                if not obj: continue
                regex = obj.groups()
            data['regex'] = regex
            return rule.get('reply').format_map(SafeDict(**data))
        return None


@bcc.receiver(GroupMessage)
async def getG(app: GraiaMiraiApplication, sender: Member, message: MessageChain):
    await rp(app, sender, 'GroupMessage', message)


@bcc.receiver(FriendMessage)
async def getF(app: GraiaMiraiApplication, sender: Friend, message: MessageChain):
    await rp(app, sender, 'FriendMessage', message)


async def rp(app: GraiaMiraiApplication, sender: T.Union[Member, Friend], event_type: "Type", message: MessageChain):
    text = formatMsg(message).strip().replace('\r', '\n')
    if text.startswith('.reply') or text.startswith('。reply'):
        app_reply = reply(app, sender, event_type)
        if event_type == 'FriendMessage':
            qq = sender.id
            group = None
        else:
            qq = None
            group = sender.group.id
        ret = Command.parseCommand(text, qq=qq, group=group)
        if ret:
            ret = MessageChain.fromSerializationString(ret)
            await app_reply(ret)
        else:
            await app_reply('添加失败，请检查语法')
    else:
        ret = Command.parse(text, sender=sender, event_type=event_type)
        if not ret: return
        ret = MessageChain.fromSerializationString(ret)
        app_reply = reply(app, sender, event_type)
        await app_reply(ret)


def formatMsg(message: MessageChain):
    result = []
    for e in message.__root__:
        if isinstance(e, Source) or isinstance(e, Quote):
            continue
        elif isinstance(e, Plain):
            result.append(e.asSerializationString().replace("[", "[_"))
        else:
            result.append(e.asSerializationString())
    return "".join(result)
