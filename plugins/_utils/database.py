import typing as T
from pathlib import Path
from pydantic import BaseModel, ValidationError

import json
from . import common

class Database(BaseModel):
    path: T.Union[str, Path]
    class Config:
        extra = 'allow'
    
    @classmethod
    def load(cls, path: T.Union[str, Path]) -> "Database":
        try:
            db: Database = cls(path=path, **common.loadJson(path))
        except (FileNotFoundError, json.JSONDecodeError, ValidationError):
            db = cls()
        return db

    def save(self, path: T.Union[str, Path, None] = None) -> None:
        if path is None: path = self.path
        result = self.dict()
        result.pop('path')
        common.saveJson(result, path)
    
    def get(self, name: str, default = None):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return default