import json
from pathlib import Path

from graia.application.logger import LoggingLogger

logger = LoggingLogger(debug=False)


def getRunningPath(return_string: bool = True):
    if return_string:
        return str(Path(__file__).resolve().parent.parent.parent)
    else:
        return Path(__file__).resolve().parent.parent.parent


def getApi():
    with open(getRunningPath(False) / 'utils' / 'data' / 'api.json', "r", encoding="utf-8") as f:
        apis = json.loads(f.read())
        f.close()
    return apis


def checkPath(path=None, create: bool = True):
    path = path.resolve()
    if path.exists(): return True
    if create:
        path.mkdir(parents=True)
        return True
    else:
        return False


def loadJson(cfgPath, logger=logger):
    config = {}
    logger.debug('加载配置文件...')
    cfgPath = str(cfgPath)
    path = Path(cfgPath)
    checkPath(path.parent)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.debug('配置加载成功')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{}')
        logger.debug('配置文件不存在，已自动创建')
    return config


def saveJson(config, cfgPath, logger=logger):
    logger.debug('保存配置文件...')
    cfgPath = str(cfgPath)
    path = Path(cfgPath)
    checkPath(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    logger.debug('保存成功')
