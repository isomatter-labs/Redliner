from PyQt6 import QtGui as qtg
import numpy as np

class TextBox:
    def __init__(self, xc:float, yc:float, w:float, h:float, angle:float, text:str):
        self.xc = xc
        self.yc = yc
        self.w = w
        self.h = h
        self.angle = angle
        self.text = text

class SrcPage:
    def __init__(self, raster:np.ndarray, width:int, height:int, text:list[TextBox]):
        self.raster = raster
        self.text = text
        self.width = width
        self.height = height


class SrcDoc:
    def __init__(self, name: str, fp: str):
        self.name = name
        self.fp = fp
        self.preview_cache = {}
        self.page_cache = {}
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

    def page(self, page: int, dpi: float) -> SrcPage:
        if dpi != self.last_dpi:
            self.page_cache.clear()
            self.last_dpi = dpi
        if page not in self.page_cache:
            raster = self._raster(page, dpi)
            self.page_cache[page] = SrcPage(raster, raster.shape[1], raster.shape[0], self._text(page))
        return self.page_cache[page]

    def _raster(self, page:int, dpi:float) -> np.ndarray:
        raise NotImplementedError

    def _text(self, page)->list[TextBox]:
        return []



from .fitz_doc import FitzDoc

SRC_DOC_TYPES = [
    FitzDoc,
]
