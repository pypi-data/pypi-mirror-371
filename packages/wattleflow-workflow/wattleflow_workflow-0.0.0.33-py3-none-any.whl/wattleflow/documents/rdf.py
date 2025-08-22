# Module Name: documents/data_frame.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains DataFrameDocument class.

from stat import filemode
from os import path, stat
from logging import NOTSET, Handler
from typing import Optional
from pandas import DataFrame
from wattleflow.concrete import Document


class RDFDocument(Document[DataFrame]):
    def __init__(self, filename: str, level: int = NOTSET, handler: Optional[Handler] = None):
        Document.__init__(self, content="", level=level, handler=handler)
        self.update_metadata(key="filename", value=filename)

    @property
    def filename(self) -> str:
        return str(self.metadata.get('filename', ''))

    @property
    def size(self) -> int:
        if self.content is None:
            return 0

        return len(self.content)
