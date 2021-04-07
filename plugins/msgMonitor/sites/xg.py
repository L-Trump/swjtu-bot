import typing as T

import aiohttp
from lxml import etree

from . import common

API = common.getApi().get('xg')


async def getNotice(page: int = 1) -> T.List[dict]:
    """
    返回以下格式：
    {
        "title": 标题
        "url": 链接地址
    }
    """
    api = API['notice']
    async with aiohttp.ClientSession() as session:
        async with session.get(api['url'], params={'page': page}) as res:
            ret = await res.text()

    html = etree.HTML(ret)
    newsLists = html.xpath(r'/html//ul[@class="block-ctxlist"]/li')
    result = []
    for x in newsLists:
        new = x.xpath('h4/a')[0]
        url = API['url'] + new.attrib['href']
        title = new.text
        date = x.xpath(r'p/span[1]/text()')[0]
        ret = {
            'url': url,
            'title': title,
            'origin': '通知公告',
            'date': date
        }
        result.append(ret)
    return result
