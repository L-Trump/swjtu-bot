import asyncio
import re
import time
import traceback
import typing as T

from graia.application import (
    GraiaMiraiApplication, MessageChain, Member, Friend)
from graia.application.logger import LoggingLogger
from graia.application.message.elements.internal import Plain
from graia.broadcast import Broadcast

from .sites import jwc, sist, xg
from .._utils import Type, reply, MESSAGE_T, ExternalElement
from .._utils.database import Database, common
from .._utils.env import env

logger = LoggingLogger()
config = Database.load(common.getRunningPath(False) / 'config' / 'msgMonitor.json')
config.xg = config.get('xg', [])
config.jwc = config.get('jwc', [])
config.sist = config.get('sist', [])
config.hello = config.get('hello', [])
config.shield = config.get('shield', {})

sub_app: GraiaMiraiApplication = env['app']
bcc: Broadcast = env['bcc']
web_list = ('jwc', 'xg', 'sist')


async def hello(app: GraiaMiraiApplication):
    msg = f"登录成功\n时间: {time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(time.time()))}"
    for item in config.hello:
        if item.get('disable', False):
            continue
        asyncio.create_task(sendMsg(app, msg, qq=item.get('qq', None), group=item.get('group', None)))


class Command:
    @classmethod
    def add(cls, web, tp, number: int):
        number = int(number)
        if web == 'all':
            [cls.add(t, tp, number) for t in web_list]
        else:
            if {tp: number} not in config.get(web, []):
                config.get(web, []).append({tp: number})

    @classmethod
    def rm(cls, web, tp, number: int):
        number = int(number)
        if web == 'all':
            [cls.rm(t, tp, number) for t in web_list]
        else:
            if {tp: number} in config.get(web, []):
                config.get(web, []).pop(config.get(web, []).index({tp: number}))

    @classmethod
    def list(cls, tp, number: int):
        it = {tp: number}
        ret = []
        for web in ('jwc', 'xg', 'sist'):
            if it in config.get(web, []): ret.append(web)
        return ret

    @classmethod
    def shield(cls, web, rule, qq=None, group=None):
        if web == 'all':
            [cls.shield(t, rule, qq=qq, group=group) for t in web_list]
        else:
            ori: str = ""
            if qq:
                ori = f"qq{qq}"
            elif group:
                ori = f"group{group}"
            if ori not in config.shield: config.shield[ori] = {}
            if web not in config.shield[ori]:
                config.shield[ori][web] = []
            config.shield[ori][web].append(rule)

    @classmethod
    def parseRule(cls, msg, rule):
        text = msg[rule.get('from', 'title')]
        if rule.get('disable', False): return False
        if 'equal' in rule and rule['equal'] != text: return False
        if 'startwith' in rule and not text.startswith(rule['startwith']): return False
        if 'endwith' in rule and not text.endswith(rule['endwith']): return False
        if 'contain' in rule and text.find(rule['contain']) == -1: return False
        if 're' in rule and not re.match(rule[re], text): return False
        return True

    @classmethod
    def check(cls, web, msg, qq=None, group=None):
        ori = ""
        if qq:
            ori = f"qq{qq}"
        elif group:
            ori = f"group{group}"
        if ori not in config.shield or web not in config.shield[ori]:
            return True
        for rule in config.shield[ori][web][-1::-1]:
            if cls.parseRule(msg, rule):
                if rule.get('unshield', False): return True
                return False
        return True


alias = {
    'group': '群',
    'qq': 'QQ',
    'xg': '扬华素质网',
    'jwc': '教务处',
    'sist': '信院',
}


@bcc.receiver("GroupMessage")
async def getG(app: GraiaMiraiApplication, sender: Member, message: MessageChain):
    await command(app, sender, "GroupMessage", message)


@bcc.receiver("FriendMessage")
async def getF(app: GraiaMiraiApplication, sender: Friend, message: MessageChain):
    await command(app, sender, "FriendMessage", message)


async def command(app: GraiaMiraiApplication, sender: T.Union[Member, Friend], event_type: "Type",
                  message: MessageChain):
    text = message.asDisplay().strip().replace('\r', '\n')
    if text.lower().startswith(r'.monitor') or text.lower().startswith(r'。monitor'):
        app_reply = reply(app, sender, event_type)
        obj = re.match(r'\s*[.。]monitor\s*(group|qq)?\s*(\d+)?\s*add\s*(xg|jwc|sist|all|hello)', text.lower(), re.I)
        if obj:
            tp, num, web = obj.groups()
            if all((web, tp, num)):
                Command.add(web, tp, num)
                await app_reply(f'已为{alias.get(tp, tp)}{num}添加{alias.get(web, web)}监控')
            elif web and not tp and not num:
                tp, num = ('qq' if event_type == 'FriendMessage' else 'group',
                           sender.id if event_type == 'FriendMessage' else sender.group.id)
                Command.add(web, tp, num)
                await app_reply(f'已为{alias.get(tp, tp)}{num}添加{alias.get(web, web)}监控')
            else:
                await app_reply('命令格式错误')
            config.save()
            return
        obj = re.match(r'\s*[.。]monitor\s*(group|qq)?\s*(\d+)?\s*rm\s*(xg|jwc|sist|all|hello)', text.lower(), re.I)
        if obj:
            tp, num, web = obj.groups()
            if all((web, tp, num)):
                Command.rm(web, tp, num)
                await app_reply(f'已为{alias.get(tp, tp)}{num}移除{alias.get(web, web)}监控')
            elif web and not tp and not num:
                tp, num = ('qq' if event_type == 'FriendMessage' else 'group',
                           sender.id if event_type == 'FriendMessage' else sender.group.id)
                Command.rm(web, tp, num)
                await app_reply(f'已为{alias.get(tp, tp)}{num}移除{alias.get(web, web)}监控')
            else:
                await app_reply('命令格式错误')
            config.save()
            return
        obj = re.match(r'[.。]monitor\s*list', text.lower())
        if obj:
            msglist = []
            msg = ""
            for item in config.jwc:
                if 'qq' in item:
                    msglist.append(f"QQ{item['qq']}")
                elif 'group' in item:
                    msglist.append(f"群{item['group']}")
            if msglist: msg = msg + f"教务处: {', '.join(msglist)}\n"
            msglist = []
            for item in config.xg:
                if 'qq' in item:
                    msglist.append(f"QQ{item['qq']}")
                elif 'group' in item:
                    msglist.append(f"群{item['group']}")
            if msglist: msg = msg + f"学工: {', '.join(msglist)}\n"
            msglist = []
            for item in config.sist:
                if 'qq' in item:
                    msglist.append(f"QQ{item['qq']}")
                elif 'group' in item:
                    msglist.append(f"群{item['group']}")
            if msglist: msg = msg + f"信院: {', '.join(msglist)}\n"
            if msg == "":
                await app_reply("暂无配置")
            else:
                await app_reply(msg[:-1])
            return
        obj = re.match(
            r'\s*[.。]monitor\s*(group|qq)?\s*(\d+)?\s*(shield|unshield)\s*(xg|jwc|sist|all)\s*(contain|startwith|endwith|equal|re)\s*([\S\s]+)',
            text, re.I)
        if obj:
            tp, num, shield, web, cmdType, cmd = obj.groups()
            unshield = False if shield.lower() == 'shield' else True
            qq = None
            group = None
            tp = tp.lower() if tp else tp
            web = web.lower() if web else web
            cmdType = cmdType.lower() if cmdType else cmdType
            if not tp:
                tp, num = ('qq' if event_type == 'FriendMessage' else 'group',
                           sender.id if event_type == 'FriendMessage' else sender.group.id)
                if event_type == 'FriendMessage':
                    qq = sender.id
                else:
                    group = sender.group.id
            else:
                if tp == 'qq':
                    qq = int(num)
                else:
                    group = int(num)
            Command.shield(web=web, rule={cmdType: cmd, 'unshield': unshield}, qq=qq, group=group)
            config.save()
            await app_reply(f"已{'取消屏蔽' if unshield else '屏蔽'}来自{alias.get(web, web)}的符合规则{cmdType}: {cmd}的消息")
            return
        await app_reply("命令格式错误")


async def JWC(app: GraiaMiraiApplication):
    olist = await jwc.getNewsList()
    errtimes = 0
    while True:
        try:
            await asyncio.sleep(10)
            nlist = await jwc.getNewsList()
            for new in nlist[:15]:
                if new in olist:
                    logger.debug('无新消息')
                    continue
                olist.append(new)
                msg = f'来源：教务处-{new["origin"]}\n标题：{new["title"]}\n链接：{new["url"]}\n时间：{new["date"]}'
                logger.info('\n' + msg + '\n')
                for item in config.jwc:
                    if item.get('disable', False): continue
                    if Command.check(web='jwc', msg=new, qq=item.get('qq', None), group=item.get('group', None)):
                        asyncio.create_task(sendMsg(app, msg, qq=item.get('qq', None), group=item.get('group', None)))
        except KeyboardInterrupt:
            break
        except Exception as e:
            errtimes += 1
            logger.debug(f'已发生{errtimes}次错误，正在重试')
            if errtimes >= 10:
                logger.error(f'尝试多次后无效，教务处查询已退出')
                logger.error(str(e))
                await sendMsg(app, f'尝试多次后无效，教务处查询已退出\n{traceback.format_exc()}', qq=171905101)
                break
        else:
            errtimes = 0


async def xgNotice(app: GraiaMiraiApplication):
    olist = await xg.getNotice()
    errtimes = 0
    while True:
        try:
            await asyncio.sleep(10)
            nlist = await xg.getNotice()
            for new in nlist[:10]:
                if new in olist:
                    logger.debug('无新消息')
                    continue
                olist.append(new)
                msg = f'来源：扬化素质网-{new["origin"]}\n标题：{new["title"]}\n链接：{new["url"]}\n时间：{new["date"]}'
                logger.info('\n' + msg + '\n')
                for item in config.xg:
                    if item.get('disable', False): continue
                    if Command.check(web='xg', msg=new, qq=item.get('qq', None), group=item.get('group', None)):
                        asyncio.create_task(sendMsg(app, msg, qq=item.get('qq', None), group=item.get('group', None)))
        except KeyboardInterrupt:
            break
        except Exception as e:
            errtimes += 1
            logger.debug(f'已发生{errtimes}次错误，正在重试')
            if errtimes >= 10:
                logger.error(f'尝试多次后无效，扬华素质网查询已退出')
                logger.error(str(e))
                await sendMsg(app, f'尝试多次后无效，扬华素质网查询已退出\n{traceback.format_exc()}', qq=171905101)
                break
        else:
            errtimes = 0


async def sistNotice(app: GraiaMiraiApplication):
    monitorList = [sist.getNotice, sist.studentWork]
    olist = {}
    for index in range(len(monitorList)):
        olist[index] = await monitorList[index]()
    errtimes = 0
    while True:
        try:
            await asyncio.sleep(10)
            for index in range(len(monitorList)):
                nlist = await monitorList[index]()
                for new in nlist[:10]:
                    if new in olist[index]:
                        logger.debug('无新消息')
                        continue
                    olist[index].append(new)
                    msg = f'来源：信院-{new["origin"]}\n标题：{new["title"]}\n链接：{new["url"]}\n时间：{new["date"]}'
                    logger.info('\n' + msg + '\n')
                    for item in config.sist:
                        if item.get('disable', False): continue
                        if Command.check(web='sist', msg=new, qq=item.get('qq', None), group=item.get('group', None)):
                            asyncio.create_task(
                                sendMsg(app, msg, qq=item.get('qq', None), group=item.get('group', None)))
        except KeyboardInterrupt:
            break
        except Exception as e:
            errtimes += 1
            logger.error(f'信院查询已发生{errtimes}次错误，正在重试')
            if errtimes >= 10:
                logger.error(f'尝试多次后无效，信院查询已退出')
                logger.error(str(e))
                await sendMsg(app, f'尝试多次后无效，信院查询已退出\n{traceback.format_exc()}', qq=171905101)
                break
        else:
            errtimes = 0


async def sendMsg(app: GraiaMiraiApplication, msg: MESSAGE_T, qq: int = None, group: int = None):
    if isinstance(msg, str):
        msg = MessageChain.create([Plain(msg)])
    if isinstance(msg, ExternalElement):
        msg = MessageChain.create([msg])
    msg = msg.asSendable()
    if qq:
        asyncio.create_task(app.sendFriendMessage(qq, msg))
    if group:
        asyncio.create_task(app.sendGroupMessage(group, msg))


asyncio.gather(hello(sub_app), JWC(sub_app), xgNotice(sub_app), sistNotice(sub_app))
