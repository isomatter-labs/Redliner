from PyQt6 import QtGui as qtg
import numpy as np

class SrcDoc:
    def __init__(self, name: str, fp: str):
        self.name = name
        self.fp = fp

    @property
    def page_count(self):
        raise NotImplementedError

    def preview(self, page: int) -> qtg.QIcon:
        raise NotImplementedError

    def raster(self, page: int, dpi: float) -> np.ndarray:
        raise NotImplementedError


from .fitz_doc import FitzDoc

SRC_DOC_TYPES = [
    FitzDoc,
]
