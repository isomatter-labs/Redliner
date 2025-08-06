from . import SrcDoc
import fitz
from PyQt6 import QtGui as qtg, QtCore as qtc
from common.constants import PREVIEW_SIZE, PREVIEW_DPI
import numpy as np

class FitzDoc(SrcDoc):
    def __init__(self, name: str, fp: str):
        super().__init__(name, fp)
        self.fp = fp
        doc: fitz.Document = fitz.open(fp)
        self._page_count = doc.page_count
        doc.close()

    @property
    def page_count(self):
        return self._page_count

    def _preview(self, page) -> qtg.QIcon:
        doc: fitz.Document = fitz.open(self.fp)
        page = doc.load_page(page)
        pix = page.get_pixmap(matrix=fitz.Matrix(PREVIEW_DPI / 72, PREVIEW_DPI / 72))
        qim = qtg.QImage(pix.samples, pix.width, pix.height, pix.stride, qtg.QImage.Format.Format_RGB888)
        px = qtg.QPixmap.fromImage(qim)
        scaled = px.scaled(PREVIEW_SIZE, qtc.Qt.AspectRatioMode.KeepAspectRatio,
                           qtc.Qt.TransformationMode.SmoothTransformation)
        doc.close()
        return qtg.QIcon(scaled)

    def _raster(self, page: int, dpi: float) -> np.ndarray:
        doc: fitz.Document = fitz.open(self.fp)
        page = doc.load_page(page)
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
        doc.close()
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
