from . import Fetcher
from redliner.common.ui import say, get_text
from PyQt6 import QtWidgets as qtw
import traceback
import os
import requests

class URLFetcher(Fetcher):
    desc = "From URL"

    def __init__(self):
        super().__init__()
        self.actions: dict[str:callable] = {"⌨️ URL": self.pick, "🌐Browse": self.pick}
        self.pd.default("path", "")
        self.pd.default("url", "https://")

    def browse(self):
        raise NotImplementedError

    def _pick(self) -> tuple[str, str]:
        url = get_text("URL", "Fetch From URL", self.pd["url"])
        if url is not None:
            self.pd["url"] = url
        return url

    def _fetch(self, target: str) -> tuple[str, str]:
        try:
            response = requests.get(target, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            recv = bytes()
            for chunk in response.iter_content(chunk_size=8192):
                recv += chunk
            fp =self.tfm.load(recv)
            return target, fp

        except requests.exceptions.RequestException as e:
            say(f"Failed to load {target}: \n\n {traceback.format_exc()}")
            return "", ""
