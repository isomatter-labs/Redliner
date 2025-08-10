from PyQt6 import QtWidgets as qtw
from redliner.common.persistent_dict import PersistentDict
from redliner.common.ui import SettingsWidget
from redliner.common import hex_to_rgb
from redliner.core.ui import DocPreview
from redliner.extensions.fetcher import FETCHER_TYPES
from redliner.extensions.source_doc import SrcDoc
from PyQt6 import QtCore as qtc, QtGui as qtg

from .render import RenderPage, RenderWidget


class DocMan(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.pd = PersistentDict()
        self.pd.default("highlighter_en", True)
        self.pd.default("highlighter_size", 4)
        self.pd.default("highlighter_sensitivity", 100)
        self.pd.default("dpi", 72)
        self.pd.default("removed_color", "#D0A000")
        self.pd.default("added_color", "#00A0D0")
        self.pd.default("highlighter_color", "#F0F000")
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
        self.lhp = DocPreview(self)
        self.rhp = DocPreview(self)
        self.lhp.signalSelectionChanged.connect(self.regen)
        self.rhp.signalSelectionChanged.connect(self.regen)
        lhl.addWidget(self.lhp)
        rhl.addWidget(self.rhp)

        self.settings = SettingsWidget([
            ["Render"],
            ["spin", "dpi", "DPI", 0, 10000],
            ["color", "removed_color", "Removed Color"],
            ["color", "added_color", "Added Color"],
            ["Highlighter"],
            ["bool", "highlighter_en", "Enabled"],
            ["spin", "highlighter_size", "Size (px)", 0, 128],
            ["spin", "highlighter_sensitivity", "Sensitivity", 0, 100],
            ["color", "highlighter_color", "Highlight Color"]
        ], 196)
        self.settings.signalSettingsChanged.connect(self.regen)
        _l.addWidget(self.settings)
        self.preview = RenderWidget(self)
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

        lh_page = self.lhp.selectedIndexes()
        rh_page = self.rhp.selectedIndexes()
        render_page = RenderPage()
        if lh_page:
            lh_page = lh_page[0].row()
            render_page.lhs = self.lhs.page(lh_page, self.settings["dpi"])
        if rh_page:
            rh_page = rh_page[0].row()
            render_page.rhs = self.rhs.page(rh_page, self.settings["dpi"])
        self.preview.set_page(render_page)

    def keyPressEvent(self, a0):
        if a0.key() == qtc.Qt.Key.Key_Home:
            self.preview.home()
        elif a0.key() == qtc.Qt.Key.Key_PageDown:
            if self.lhp.count():
                sel = self.lhp.selectedIndexes()
                if sel:
                    idx = sel[0].row()
                    idx += 1
                    if idx > self.lhp.count()-1:
                        idx = 0
                else:
                    idx = 0
                self.lhp.item(idx).setSelected(True)
            if self.rhp.count():
                sel = self.rhp.selectedIndexes()
                if sel:
                    idx = sel[0].row()
                    idx += 1
                    if idx > self.rhp.count()-1:
                        idx = 0
                else:
                    idx = 0
                self.rhp.item(idx).setSelected(True)

        elif a0.key() == qtc.Qt.Key.Key_PageUp:
            if self.lhp.count():
                sel = self.lhp.selectedIndexes()
                if sel:
                    idx = sel[0].row()
                    idx -= 1
                    if idx <0:
                        idx = self.lhp.count()-1
                else:
                    idx = self.lhp.count()-1
                self.lhp.item(idx).setSelected(True)
            if self.rhp.count():
                sel = self.rhp.selectedIndexes()
                if sel:
                    idx = sel[0].row()
                    idx -= 1
                    if idx < 0:
                        idx = self.rhp.count()-1
                else:
                    idx = self.rhp.count()-1
                self.rhp.item(idx).setSelected(True)
        elif a0.key() == qtc.Qt.Key.Key_Escape:
            sel = self.lhp.selectedIndexes()
            if sel:
                self.lhp.item(sel[0].row()).setSelected(False)
            sel = self.rhp.selectedIndexes()
            if sel:
                self.rhp.item(sel[0].row()).setSelected(False)

        else:
            super().keyPressEvent(a0)

