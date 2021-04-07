import aiohttp
import base64
import typing as T
from sys import version_info

# 图鉴接码初始化http://www.ttshitu.com/
OCR_UNAME = "yinghaochi"
OCR_PWD = "Chichi0077!!"


class OcrError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self) -> str:
        return f"验证码识别失败Message: {self.msg}"


async def ocr(img: bytes) -> T.Dict[str]:
    # img = img.convert('RGB')
    # buffered = BytesIO()
    # img.save(buffered, format="JPEG")
    if version_info.major >= 3:
        b64 = str(base64.b64encode(img), encoding='utf-8')
    else:
        b64 = str(base64.b64encode(img))
    data = {
        "username": OCR_UNAME,
        "password": OCR_PWD,
        "typeid": "3",
        "image": b64
    }
    async with aiohttp.request('POST', "http://api.ttshitu.com/base64", json=data) as r:
        result = await r.json()
    if result['success']:
        ret = {
            'code': result["data"]["result"],
            'id': result["data"]["id"]
        }
        return ret
    else:
        raise OcrError(result['message'])


async def reportError(ocrId: str) -> str:
    data = {"id": ocrId}
    async with aiohttp.request('POST', "http://api.ttshitu.com/reporterror.json", json=data) as r:
        result = await r.json()
    if result['success']:
        return "验证码识别错误，报错成功"
    else:
        return result["message"]
