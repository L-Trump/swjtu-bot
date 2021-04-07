import asyncio
import typing as T

import weasyprint as wsp
from graia.application import (
    GraiaMiraiApplication, Friend,
    Image, Member,
    MessageChain
)
from graia.application.message.elements.internal import Plain
from graia.broadcast import Broadcast

from .._utils import at_me, common
from .._utils.env import env

sub_app: GraiaMiraiApplication = env['app']
bcc: Broadcast = env['bcc']
imgPath = common.getRunningPath(False) / 'data' / 'image' / 'temp_course.png'

courseTable: T.Optional[Image] = None


async def getCourse():
    global courseTable
    while True:
        html = wsp.HTML(
            url='http://jwc.swjtu.edu.cn/vatuu/CourseAction?setAction=printCourseTable&viewType=view&queryType=class&key=0403202002&key_name=%E9%80%9A%E4%BF%A12020-02%E7%8F%AD&input_term_id=98&input_term_name=2020-2021%E7%AC%AC2%E5%AD%A6%E6%9C%9F')
        css = wsp.CSS(string='''
@page {
    size: 1500px 627px;
    margin: 0 0 0 0;
    border: 50px 0 0 0;
}
''')
        html.write_png(str(imgPath), stylesheets=[css], presentational_hints=True)
        courseTable = Image.fromLocalFile(imgPath)
        await asyncio.sleep(86400)


timeTable = """上课时间
• 第1节：08:00-08:45
• 第2节：08:50-09:35
• 第3节：09:50-10:35
• 第4节：10:40-11:25
• 第5节：11:30-12:15
• 第6节：14:00-14:45
• 第7节：14:50-15:35  
• 第8节：15:50-16:35
• 第9节：16:40-17:25
• 第10节：17:30-18:15
• 第11节：19:30-20:15
• 第12节：20:20-21:05
• 第13节：21:10-21:55"""


@bcc.receiver("FriendMessage")
async def replyFriend(app: GraiaMiraiApplication, sender: Friend, message: MessageChain):
    keywords = ['课程表', '.course', 'course']
    text = message.asDisplay().strip().lower().replace('\r', '\n')
    if (text in keywords) or (at_me(app, message) and any([keyword in text for keyword in keywords])):
        msg = MessageChain.create([courseTable, Plain(timeTable)])
        await app.sendFriendMessage(sender, msg)


@bcc.receiver("GroupMessage")
async def replyGroup(app: GraiaMiraiApplication, sender: Member, message: MessageChain):
    keywords = ['课程表', '.course', 'course']
    text = message.asDisplay().strip().lower().replace('\r', '\n')
    if (text in keywords) or (at_me(app, message) and any([keyword in text for keyword in keywords])):
        msg = MessageChain.create([courseTable, Plain(timeTable)])
        await app.sendGroupMessage(sender.group, msg)


asyncio.gather(getCourse())
