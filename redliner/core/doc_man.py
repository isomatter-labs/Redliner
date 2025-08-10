from PyQt6 import QtWidgets as qtw
from redliner.common.persistent_dict import PersistentDict
from redliner.core.ui import DocPreview
from redliner.extensions.fetcher import FETCHER_TYPES
from redliner.extensions.source_doc import SrcDoc
from PyQt6 import QtCore as qtc, QtGui as qtg

from .render import Renderer, RenderPage



def rgb_to_hex(red: int, green: int, blue: int, alpha: int | None = None) -> str:
    return f"#{hex(red)[2:].zfill(2)}{hex(green)[2:].zfill(2)}{hex(blue)[2:].zfill(2)} {alpha if alpha is not None else ''}"

def hex_to_rgb(val:str) -> tuple:
    val = val.strip().lower()
    if val[0] == "#":
        val = val[1:]
    r1, r2, g1, g2, b1, b2 = val
    return (int(r1+r2,16), int(g1+g2,16), int(b1+b2,16))

class ColorButton(qtw.QPushButton):
    signalColorChanged = qtc.pyqtSignal(str)

    def __init__(self, hex):
        super().__init__()
        self.hx = hex
        self.setStyleSheet(f"background-color:{self.hx}")
        self.setText(self.hx)
        self.clicked.connect(self.color_pick)

    def color_pick(self):
        color_pick = qtw.QColorDialog.getColor(qtg.QColor(self.hx))
        r, g, b, a = color_pick.getRgb()
        self.hx = rgb_to_hex(r, g, b)
        self.setStyleSheet(f"background-color:{self.hx}")
        self.setText(self.hx)
        self.signalColorChanged.emit(self.hx)


class SettingsWidget(qtw.QWidget):
    signalSettingsChanged = qtc.pyqtSignal()
    def __init__(self, items:list, width:int):
        super().__init__()
        self.pd = PersistentDict()
        self._l = qtw.QVBoxLayout(self)
        self._l.setContentsMargins(0,0,0,0)
        self._l.setSpacing(2)
        self.setFixedWidth(width)
        tgt_l = self._l
        for row in items:
            if len(row) == 1:
                gb = qtw.QGroupBox(row[0])
                gb_l = qtw.QVBoxLayout(gb)
                self._l.addWidget(gb)
                tgt_l = gb_l
            else:
                _type, key, name, *args = row
                val = self.pd[key]
                _r = qtw.QWidget()
                _l = qtw.QHBoxLayout(_r)
                _l.setContentsMargins(0,0,0,0)
                _l.setSpacing(2)
                lb = qtw.QLabel(name)
                _l.addWidget(lb)
                lb.setSizePolicy(qtw.QSizePolicy.Policy.Fixed, qtw.QSizePolicy.Policy.Fixed)
                if _type == "bool":
                    w = qtw.QCheckBox()
                    w.setChecked(val)
                    w.stateChanged.connect(lambda *_, _k=key, _w=w: self.set(_k, _w.isChecked()))
                if _type == "spin":
                    w = qtw.QSpinBox()
                    w.setRange(*args)
                    w.setValue(val)
                    w.valueChanged.connect(lambda *_, _k=key, _w=w: self.set(_k, _w.value()))
                if _type == "color":
                    w = ColorButton(val)
                    w.signalColorChanged.connect(lambda *_, _k=key, _w=w: self.set(_k, _w.hx))
                _l.addWidget(w)
                tgt_l.addWidget(_r)
        self._l.addStretch()

    def set(self, key, value):
        self.pd[key] = value
        self.signalSettingsChanged.emit()

    def __getitem__(self, key):
        return self.pd[key]

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
        self.lhp = DocPreview()
        self.rhp = DocPreview()
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
        self.renderer = Renderer()
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

        lh_page = self.lhp.selectedIndexes()
        rh_page = self.rhp.selectedIndexes()
        render_page = RenderPage()
        if lh_page:
            lh_page = lh_page[0].row()
            render_page.lhs = self.lhs.page(lh_page, self.settings["dpi"])
        if rh_page:
            rh_page = rh_page[0].row()
            render_page.rhs = self.rhs.page(rh_page, self.settings["dpi"])
        self.renderer.set_page(render_page)
        self.redraw()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.redraw()

    def redraw(self, lh=True, rh=True):

        px = self.renderer.render(hex_to_rgb(self.settings["added_color"]),
                                  hex_to_rgb(self.settings["removed_color"]),
                                  hex_to_rgb(self.settings["highlighter_color"]),
                                  self.settings["highlighter_en"],
                                  1-self.settings["highlighter_sensitivity"]/100,
                                  self.settings["highlighter_size"],
                                  0,
                                  0,
                                  1,
                                  0,
                                  lh,
                                  rh,
                                  self.preview.width(),
                                  self.preview.height())
        self.preview.setPixmap(qtg.QPixmap.fromImage(px))
        self.preview.setMinimumSize(qtc.QSize(64, 64))

    def keyPressEvent(self, a0):
        if a0.key() == qtc.Qt.Key.Key_Left:
            self.redraw(rh=False)
        if a0.key() == qtc.Qt.Key.Key_Right:
            self.redraw(lh=False)
        super().keyPressEvent(a0)

    def keyReleaseEvent(self, a0):
        self.redraw()


