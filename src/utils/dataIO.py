import json

from pathlib import Path


class DataIO:

    @classmethod
    def readJsonData(cls, path: Path) -> dict|list:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
