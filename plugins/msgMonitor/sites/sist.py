import typing as T

import aiohttp
from lxml import etree

from . import common

API = common.getApi().get('sist')


async def getNotice(navId: int = 46, page: int = 1, origin: str = '本科生公告') -> T.List[dict]:
    """
    返回以下格式：
    {
        "title": 标题
        "origin": 来源
        "
        "url": 链接地址
    }
    """
    api = API['notice']
    data = {
        "curPage": page,
        "pageMethod": "jumpPage",
        "navId": navId
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api['url'], data=data) as res:
            ret = await res.text()

    html = etree.HTML(ret)
    newsLists = html.xpath(r'/html//dd')
    result = []
    for x in newsLists:
        new = x.xpath('div/a')[0]
        url = new.attrib['href']
        title = new.attrib['title']
        date = x.xpath(r'span/text()')[0]
        ret = {
            'url': url,
            'title': title,
            'origin': origin,
            'date': date
        }
        result.append(ret)
    return result


async def graduateNotice(page: int = 1) -> T.List[dict]:
    return await getNotice(navId=163, page=page, origin='本科毕业设计')


async def studentWork(page: int = 1) -> T.List[dict]:
    return await getNotice(navId=77, page=page, origin='学生工作公告')
