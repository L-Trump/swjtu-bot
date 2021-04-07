import importlib
import typing as T
from pathlib import Path

from graia.application.logger import LoggingLogger

logger = LoggingLogger(debug=False)


def load_plugins(debug: T.Optional[T.List[str]] = None):
    plugin_dir = Path(__file__).parent
    module_prefix = plugin_dir.name

    if debug:
        [load_plugin(f'{module_prefix}.{p}') for p in debug]
        return
    for plugin in plugin_dir.iterdir():
        if plugin.is_dir() \
                and not plugin.name.startswith('_') \
                and plugin.joinpath('__init__.py').exists() \
                and not plugin.joinpath('.disable').exists():
            load_plugin(f'{module_prefix}.{plugin.name}')


# noinspection PyUnusedLocal
def load_plugin(module_path: str):
    try:
        module = importlib.import_module(module_path)
        # 无需调用app.include_others()，否则会导致重复注册事件，原理不明
        # app.include_others(module.sub_app)
        logger.info(f'Succeeded to import "{module_path}"')
    except Exception as e:
        logger.error(f'Failed to import "{module_path}", error: {e}')
        logger.exception(e)
