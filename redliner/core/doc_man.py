from PyQt6 import QtWidgets as qtw
from common.persistent_dict import PersistentDict
from core.ui import DocPreview
from extensions.fetcher import FETCHER_TYPES
from extensions.source_doc import SrcDoc
from .diff import diff
import numpy as np
from PyQt6 import QtCore as qtc, QtGui as qtg

class DocMan(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.pd = PersistentDict()
        self.pd.default("scale_lo", 0)
        self.pd.default("scale_hi", 255)
        self.pd.default("dpi", 72)
        self.lhs = None
        self.rhs = None
        self.click_side = "L"
        _l = qtw.QHBoxLayout(self)
        _l.setContentsMargins(0, 0, 0, 0)
        _l.setSpacing(2)
        lhw = qtw.QGroupBox("Old")
        lhw.setFixedWidth(144)
        rhw = qtw.QGroupBox("New")
        rhw.setFixedWidth(144)

        lhl = qtw.QVBoxLayout(lhw)
        lhl.setContentsMargins(2, 2, 2, 2)
        lhl.setSpacing(2)
        rhl = qtw.QVBoxLayout(rhw)
        rhl.setContentsMargins(2, 2, 2, 2)
        rhl.setSpacing(2)
        _l.addWidget(lhw)
        _l.addWidget(rhw)
        self.lhp = DocPreview()
        self.rhp = DocPreview()
        self.lhp.signalSelectionChanged.connect(self.regen)
        self.rhp.signalSelectionChanged.connect(self.regen)
        lhl.addWidget(self.lhp)
        rhl.addWidget(self.rhp)

        w_settings = qtw.QWidget()
        _l.addWidget(w_settings)
        l_s = qtw.QGridLayout(w_settings)
        self.sb_dpi = qtw.QSpinBox()
        self.sb_dpi.setRange(0, 10000)
        self.sb_dpi.setValue(self.pd["dpi"])
        self.sb_dpi.valueChanged.connect(self.regen)
        l_s.addWidget(qtw.QLabel("DPI"), 0, 0)
        l_s.addWidget(self.sb_dpi, 0, 1)
        self.sb_lo = qtw.QSpinBox()
        self.sb_lo.setRange(0, 254)
        self.sb_lo.setValue(self.pd["scale_lo"])
        self.sb_lo.valueChanged.connect(self.regen)
        l_s.addWidget(qtw.QLabel("Lower Thresh"), 1, 0)
        l_s.addWidget(self.sb_lo, 1, 1)

        self.sb_hi = qtw.QSpinBox()
        self.sb_hi.setRange(1, 255)
        self.sb_hi.setValue(self.pd["scale_hi"])
        self.sb_hi.valueChanged.connect(self.regen)
        l_s.addWidget(qtw.QLabel("Upper Thresh"), 2, 0)
        l_s.addWidget(self.sb_hi, 2, 1)
        l_s.setRowStretch(3, 1)
        w_settings.setFixedWidth(196)
        self.preview = qtw.QLabel()
        self.preview.setScaledContents(True)
        _l.addWidget(self.preview)
        self.fetchers = {f.desc: f for f in [F() for F in FETCHER_TYPES]}

        for k, v in self.fetchers.items():
            v.signalDocReady.connect(self.doc_ready)
            gb = qtw.QGroupBox(k)
            gbl = qtw.QVBoxLayout(gb)
            gbl.setContentsMargins(2, 2, 2, 2)
            gbl.setSpacing(2)
            for name, act in v.actions.items():
                pb = qtw.QPushButton(name)
                pb.clicked.connect(lambda: self.__setattr__("click_side", "L"))
                pb.clicked.connect(lambda *args, _a=act: _a())
                gbl.addWidget(pb)

            lhl.addWidget(gb)
            gb = qtw.QGroupBox(k)
            gbl = qtw.QVBoxLayout(gb)
            gbl.setContentsMargins(2, 2, 2, 2)
            gbl.setSpacing(2)
            for name, act in v.actions.items():
                pb = qtw.QPushButton(name)
                pb.clicked.connect(lambda: self.__setattr__("click_side", "R"))
                pb.clicked.connect(act)
                gbl.addWidget(pb)
            rhl.addWidget(gb)

    def doc_ready(self, doc: SrcDoc):
        if doc is None:
            return
        if self.click_side == "L":
            self.lhs = doc
            self.lhp.set_doc(doc)
        else:
            self.rhs = doc
            self.rhp.set_doc(doc)

    def regen(self):
        scale_lo = self.sb_lo.value()
        scale_hi = self.sb_hi.value()
        dpi = self.sb_dpi.value()
        if scale_hi <= scale_lo:
            if scale_lo != self.pd["scale_lo"]:
                # low scale was changed
                scale_hi = scale_lo + 1
                self.sb_hi.setValue(scale_hi)
            else:
                scale_lo = scale_hi - 1
                self.sb_lo.setValue(scale_lo)
        self.pd.update({
            "dpi": dpi,
            "scale_lo": scale_lo,
            "scale_hi": scale_hi
        })
        lh_page = self.lhp.selectedIndexes()
        lh_data = None
        rh_data = None
        if lh_page:
            lh_page = lh_page[0].row()
            lh_data = self.lhs.raster(lh_page, dpi)
        rh_page = self.rhp.selectedIndexes()
        if rh_page:
            rh_page = rh_page[0].row()
            rh_data = self.rhs.raster(rh_page, dpi)
        if lh_data is not None:
            if rh_data is not None:
                im = diff(lh_data, rh_data, scale_lo, scale_hi)
            else:
                im = lh_data
        elif rh_data is not None:
            im = rh_data
        else:
            im = np.full((256, 256, 3), (0, 0, 255), dtype=np.uint8)
        image = qtg.QImage(im, im.shape[1], im.shape[0], im.strides[0], qtg.QImage.Format.Format_RGB888)
        self.preview.setPixmap(qtg.QPixmap.fromImage(image))
        self.preview.setMinimumSize(qtc.QSize(64, 64))
