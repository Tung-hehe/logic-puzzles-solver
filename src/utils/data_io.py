import json

from pathlib import Path


class DataIO:

    @classmethod
    def read_json_data(cls, path: Path) -> dict|list:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
