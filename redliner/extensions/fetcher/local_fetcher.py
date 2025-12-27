from . import Fetcher
from redliner.common.ui import say
from PySide6 import QtWidgets as qtw
import traceback
import os

class LocalFetcher(Fetcher):
    desc = "Local File"

    def __init__(self):
        super().__init__()
        self.actions: dict[str:callable] = {"📂Open": self.pick}
        self.pd.default("path", "")

    def _pick(self) -> str:
        file_path, _ = qtw.QFileDialog.getOpenFileName(None,
                                                       "Select a file",  # Dialog title
                                                       self.pd["path"],  # Initial directory (empty string for default)
                                                       "All Files (*)"  # File filters
                                                       )
        if os.path.exists(file_path):
            head, _ = os.path.split(file_path)
            self.pd["path"] = head
            return file_path

    def _fetch(self, target: str) -> tuple[str, str]:
        try:
            file_pointer = self.tfm.load(target)
            return target, file_pointer
        except:
            say(f"Failed to load '{target}':\n{traceback.format_exc()}")
            return "", ""