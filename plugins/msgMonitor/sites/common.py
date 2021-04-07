import json
from pathlib import Path
import typing as T


def getRunningPath(return_string: bool = True) -> T.Union[str, Path]:
    if return_string:
        return str(Path(__file__).resolve().parent.parent)
    else:
        return Path(__file__).resolve().parent.parent


def getApi() -> dict:
    with open(Path(__file__).resolve().parent / 'data' / 'api.json', "r", encoding="utf-8") as f:
        apis = json.loads(f.read())
        f.close()
    return apis


def checkPath(path: T.Optional[T.Union[Path, str]] = None, create: bool = True) -> bool:
    if not path: return False
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()
    if path.exists():
        return True
    if create:
        path.mkdir(parents=True)
        return True
    else:
        return False
