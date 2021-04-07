import typing as T

import aiohttp
from lxml import etree

from . import common

API = common.getApi().get('jwc')


async def getNewsList(jumpPage: int = 1) -> T.List[dict]:
    """
    返回以下格式：
    {
        "title": 标题,
        "url": 链接地址,
        "origin": 来源,
        "date": 日期
    }
    """
    api = API['newsList']
    async with aiohttp.ClientSession() as session:
        async with session.get(api['url'], params={'jumpPage': jumpPage}) as res:
            ret = await res.text()

    html = etree.HTML(ret)
    newsLists = html.xpath(r'/html//div[@class="newsSearchMainDiv"]//div[@class="littleResultDiv"]')
    result = []
    for x in newsLists:
        new = x.xpath(r'h3/a')[0]
        url = API['url'] + new.attrib['href'][2:]
        title = new.text
        origin = x.xpath(r'p/span[3]/text()')[0]
        date = x.xpath(r'p/span[1]/text()')[0]
        ret = {
            'url': url,
            'title': title,
            'origin': origin,
            'date': date
        }
        result.append(ret)
    return result
