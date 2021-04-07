import re
import time

from graia.application import (
    GraiaMiraiApplication, GroupMessage,
    Image,
    Friend, Member,
    FriendMessage,
    MessageChain
)
from graia.application.logger import LoggingLogger
from graia.application.message.elements.internal import Plain
from graia.broadcast import Broadcast

from . import pic
from .Exceptions import LoginException, JwcException
from .vatu import Vatu
from .._utils import at_me, common
from .._utils.database import Database
from .._utils.env import env

logger = LoggingLogger()
sub_app: GraiaMiraiApplication = env['app']
bcc: Broadcast = env['bcc']
imgDir = common.getRunningPath(False) / 'data' / 'image' / 'privateCourse'
common.checkPath(imgDir)
config = Database.load(common.getRunningPath(False) / 'config' / 'privateCourse.json')


class Command:
    @classmethod
    async def parseCommand(cls, text: str, qq: int = None, group: int = None):
        obj = re.match(r'\s*[.。](group|own)course\s*(qq|group)?\s*(\d+)?\s*(login|logout|status)?\s*(\d+)?\s*(\S+)?',
                       text, re.I)
        if not obj:
            return False
        mode, sp, num, op, user, pwd = obj.groups()
        if sp:
            if sp.strip().lower() == 'qq' and num:
                qq = num
            elif sp.strip().lower() == 'group' and num:
                group = num
        if not all((mode, op)) or not any((qq, group)):
            return False
        mode = mode.strip().lower()
        op = op.strip().lower()
        tag = f'qq{qq}' if mode == 'own' else f'group{group}'
        if op == 'login':
            if not all((user, pwd)):
                return False
            account = Vatu(user, pwd)
            try:
                await account.login()
            except LoginException as e:
                await account.close()
                return e.msg
            finally:
                await account.close()
            msg = '登录成功' if not hasattr(config, tag) else '登录成功，已覆盖原有账号信息'
            cls.add(tag, user, pwd)
            return msg
        elif op == 'logout':
            cls.rm(tag)
            return '登出成功'
        elif op == 'status':
            u = cls.info(tag)
            if u:
                return '当前登录账号: {}'.format(u)
            else:
                return '当前无账号登录'
        else:
            return False

    @staticmethod
    def add(tag: str, user: str, pwd: str):
        setattr(config, tag, {'user': user, 'pwd': pwd})
        config.save()

    @staticmethod
    def rm(tag: str):
        if hasattr(config, tag):
            delattr(config, tag)
            config.save()

    @staticmethod
    def info(tag):
        if hasattr(config, tag):
            return config.get(tag)['user']
        else:
            return None


async def getCourseTable(item):
    if not hasattr(config, item):
        return Plain(f'未设置账号，请使用.owncourse login 账号 密码 登录\n设置群公共账号使用.groupcourse')
    else:
        imgPath = imgDir / f'{getattr(config, item)["user"]}-{time.strftime("%Y-%m-%d", time.localtime(time.time()))}.jpg'
        if not imgPath.exists():
            user = config.get(item)['user']
            pwd = config.get(item)['pwd']
            account = Vatu(user, pwd)
            try:
                await account.login()
                html = await account.courseTable()
            except JwcException as e:
                await account.close()
                return e.msg
            finally:
                await account.close()
            f = pic.toImage(html)
            imgPath.write_bytes(f.getbuffer())
        return Image.fromLocalFile(imgPath)


@bcc.receiver(FriendMessage)
async def reFriend(app: GraiaMiraiApplication, sender: Friend, message: MessageChain):
    text = message.asDisplay().strip().replace('\r\n', '\n').replace('\r', '\n')
    keywords = ['个人课表', '个人课程表', 'selfcourse', 'owncourse', 'self course', 'own course', 'privatecourse']
    if any([text.lower().startswith(opt) for opt in ('.owncourse', '。owncourse', '.groupcourse', '。groupcourse')]):
        msg = await Command.parseCommand(text, qq=sender.id)
        if not msg:
            msg = '命令执行失败，请检查格式'
        await app.sendFriendMessage(sender, MessageChain.create([Plain(msg)]))
    elif (text.lower() in keywords) or at_me(app, message) and any(keyword in text.lower() for keyword in keywords):
        await app.sendFriendMessage(sender, MessageChain.create([await getCourseTable(f'qq{sender.id}')]))


@bcc.receiver(GroupMessage)
async def reGroup(app: GraiaMiraiApplication, sender: Member, message: MessageChain):
    text = message.asDisplay().strip().replace('\r', '\n')
    keywords = ['个人课表', '个人课程表', 'selfcourse', 'owncourse', 'self course', 'own course', 'privatecourse']
    keywords_group = ['群课表', '群课程表', 'groupcourse', 'ourcourse', 'our course', 'group course', 'publiccourse']
    if any([text.lower().startswith(opt) for opt in ('.owncourse', '。owncourse', '.groupcourse', '。groupcourse')]):
        msg = await Command.parseCommand(text, qq=sender.id, group=sender.group.id)
        if not msg:
            msg = '命令执行失败，请检查格式'
        await app.sendGroupMessage(sender.group, MessageChain.create([Plain(msg)]))
    elif (text.lower() in keywords) or (at_me(app, message) and any([keyword in text.lower() for keyword in keywords])):
        await app.sendGroupMessage(sender.group, MessageChain.create([await getCourseTable(f'qq{sender.id}')]))
    elif (text.lower() in keywords_group) or (
            at_me(app, message) and any([keyword in text.lower() for keyword in keywords_group])):
        await app.sendGroupMessage(sender.group, MessageChain.create([await getCourseTable(f'group{sender.group.id}')]))
