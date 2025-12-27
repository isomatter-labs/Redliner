from PySide6 import QtCore as qtc
import logging
import traceback

from redliner.common.temporary_file_manager import  TemporaryFileManager
from redliner.common.persistent_dict import PersistentDict
from redliner.common.ui import say
from redliner.extensions.source_doc import SrcDoc, SRC_DOC_TYPES

class Fetcher(qtc.QObject):
    desc = ""
    signalDocReady = qtc.Signal(SrcDoc)

    def __init__(self):
        super().__init__()
        self.pd = PersistentDict()
        self.tfm = TemporaryFileManager()
        self.actions: dict[str:callable] = {}

    def pick(self) -> SrcDoc:
        return self.fetch(self._pick())

    def _pick(self) -> str:
        raise NotImplementedError

    def fetch(self, target: str) -> SrcDoc | None:
        if target is None:
            return None
        name, fp = self._fetch(target)
        for Cls in SRC_DOC_TYPES:
            try:
                self.signalDocReady.emit(Cls(name, fp))
                return
            except:
                logging.warning(traceback.format_exc())
        say(f"Failed to load {target}! Unknown file type.")

    def _fetch(self, target) -> tuple[str, str]:
        raise NotImplementedError

    def action(self, action: str):
        self.actions[action]()

from .local_fetcher import LocalFetcher
from .url_fetcher import URLFetcher
FETCHER_TYPES = [
    LocalFetcher,
    URLFetcher
]
