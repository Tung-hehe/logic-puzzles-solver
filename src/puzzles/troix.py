import itertools

from pathlib import Path

import mip

from .model import Model

from src.utils import PuzzleName, Colors


class Troix(Model):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath, PuzzleName.Binox)
        return None
