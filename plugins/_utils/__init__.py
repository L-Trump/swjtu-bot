import typing as T
from datetime import datetime, timedelta

from pydantic import BaseModel
from graia.application import (
    GraiaMiraiApplication, Member, Friend,
    MessageChain
)
from graia.application.message.elements import ExternalElement
from graia.application.message.elements.internal import (At, Plain)
from graia.application.message.elements import Element
from .alias import MESSAGE_T

# https://mirai-py.originpages.com/tutorial/annotations.html
Sender = T.Union[Member, Friend]
Type = str


def reply(app: GraiaMiraiApplication, sender: "Sender", event_type: "Type"):
    """app_reply = reply(app, sender, event_type)
    app_reply(message)
    """

    async def wrapper(message: MESSAGE_T, *, at_sender: bool = False):
        if isinstance(message, ExternalElement):
            message = MessageChain.create([message])
        if isinstance(message, str):
            message = MessageChain.create([Plain(message)])
        if at_sender:
            if isinstance(message, MessageChain):
                message = MessageChain.join(MessageChain.create([At(Sender.id)]), message)
            else:
                raise TypeError(f"not supported type for reply: {message.__class__.__name__}")
        message = message.asSendable()
        if event_type == "GroupMessage":
            await app.sendGroupMessage(sender.group, message)
        elif event_type == "FriendMessage":
            await app.sendFriendMessage(sender, message)
        else:
            raise ValueError("Not supported event type")

    return wrapper


def at_me(app: GraiaMiraiApplication, message: MessageChain):
    try:
        at: T.Optional[T.Union[At, Element]] = message.getFirst(At)
    except IndexError:
        return False
    except:
        raise
    if at:
        return at.target == app.connect_info.account
    else:
        return False


class CoolDown(BaseModel):
    """example:
    cd = CoolDown(app='app1', td=20)
    cd.update(123)
    cd.check(123)
    """
    app: str
    td: float  # timedelta
    value: T.Dict[int, datetime] = {}

    def update(self, mid: int) -> None:
        self.value.update({mid: datetime.now()})

    def check(self, mid: int) -> bool:
        ret = datetime.now() >= self.value.get(mid, datetime.utcfromtimestamp(0)) + timedelta(seconds=self.td)
        return ret


def shuzi2number(shuzi: T.Optional[str]) -> int:
    s = {'一': 1, '两': 2, '二': 2, '三': 3,
         '四': 4, '五': 5, '六': 6, '七': 7,
         '八': 8, '九': 9, '十': 10}
    if not shuzi:
        return 1
    elif shuzi.isdecimal():
        return int(shuzi)
    elif shuzi in s.keys():
        return s[shuzi]
    else:
        return 1
