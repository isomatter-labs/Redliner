from PyQt6 import QtGui as qtg
import numpy as np

class SrcDoc:
    def __init__(self, name: str, fp: str):
        self.name = name
        self.fp = fp
        self.preview_cache = {}
        self.raster_cache = {}
        self.last_dpi = 0

    @property
    def page_count(self):
        raise NotImplementedError

    def preview(self, page: int) -> qtg.QIcon:
        if page not in self.preview_cache:
            self.preview_cache[page] = self._preview(page)
        return self.preview_cache[page]


    def _preview(self, page:int):
        raise NotImplementedError

    def raster(self, page: int, dpi: float) -> np.ndarray:
        if dpi != self.last_dpi:
            self.raster_cache.clear()
            self.last_dpi = dpi
        if page not in self.raster_cache:
            self.raster_cache[page] = self._raster(page, dpi)
        return self.raster_cache[page]

    def _raster(self, page:int, dpi:float):
        raise NotImplementedError

from .fitz_doc import FitzDoc

SRC_DOC_TYPES = [
    FitzDoc,
]
