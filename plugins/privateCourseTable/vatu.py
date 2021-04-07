import json
import time

import typing as T
import aiohttp
from graia.application.logger import LoggingLogger
from lxml import etree

from . import ttocr
from .Exceptions import LoginException, CourseQueryException

logger = LoggingLogger()
url_code = r'http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG?test={}'
url_login = r'http://jwc.swjtu.edu.cn/vatuu/UserLoginAction'
url_login2 = r'http://jwc.swjtu.edu.cn/vatuu/UserLoadingAction'
url_index = r'http://jwc.swjtu.edu.cn/service/login.html'
url_course = r'http://jwc.swjtu.edu.cn/vatuu/CourseAction'


class Vatu(object):
    s: T.Optional[aiohttp.ClientSession] = None
    logged: bool = False
    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.s = aiohttp.ClientSession()

    async def login(self, username: str = None, password: str = None):
        if username is None:
            username = self.username
            password = self.password
        elif password is None:
            raise LoginException(msg='不允许空密码')

        loginData = {
            'username': username,
            'password': password,
            'url': None,
            'returnType': None,
            'returnUrl': None,
            'area': None,
        }
        headers = {
            'Referer': url_index,
        }
        await self.s.head('http://jwc.swjtu.edu.cn/service/login.html')
        while True:
            async with self.s.get(url_code.format(int(time.time()))) as ret:
                img = await ret.read()
            code, ocrId = (await ttocr.ocr(img)).values()
            loginData['ranstring'] = code
            async with self.s.post(url_login, data=loginData, headers=headers) as r:
                result = await r.text()
            result = json.loads(result)
            if int(result['loginStatus']) == 1:
                self.logged = True
                msg = result['loginMsg']
                logger.info(result['loginMsg'])
                break
            elif result['loginMsg'] == '验证码输入不正确':
                await ttocr.reportError(ocrId)
            else:
                raise LoginException(int(result['loginStatus']), result['loginMsg'])
        data = {
            'url': r'http://jwc.swjtu.edu.cn/service/login.jsp',
            'returnUrl': None,
            'returnType': None,
            'loginMsg': msg,
        }
        await self.s.post(url_login2, data=data)

    async def courseTable(self, num: T.Union[str, int] = ''):
        if not self.logged:
            raise CourseQueryException('未登录')
        data = {
            'setAction': 'userCourseScheduleTable',
            'viewType': 'studentCourseTableWeek',
            'selectTableType': 'ThisTerm',
            'queryType': 'student',
            'weekNo': num,
        }
        async with self.s.post(url_course, data=data) as r:
            ret = await r.text()
        html = etree.HTML(ret)
        table = html.xpath('//table')[0]
        return etree.tostring(table, encoding="utf-8", pretty_print=True, method="html").decode("utf-8")

    async def close(self):
        await self.s.close()
# print('---------------')
# print(s.cookies)
# ret = s.post(url_login, data = loginData, headers = headers)
# print('---------------')
# print(ret.json())
# print('---------------')

# async def main():
# account = Vatu('2020112456', 'Chichi007!!')
# try:
# await account.login()
# html = await account.courseTable()
# print(html)
# f = toImage(html)
# p = Path(__file__).resolve().parent / '2.jpg'
# p.write_bytes(f.getbuffer())
# except KeyboardInterrupt:
# logger.warning('用户按键退出')
# except JwcException as e:
# logger.error(str(e))
# finally:
# await account.close()

# if __name__=='__main__':
# asyncio.run(main())
