from PySide6 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
import logging

from redliner.common.persistent_dict import PersistentDict
from redliner.common import rgb_to_hex

_logger = logging.getLogger(__name__)


def say(message: str, title=""):
    msg = qtw.QMessageBox()
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.exec()


def get_text(message: str = "", title: str = "", start_string: str = ""):
    text, ok = qtw.QInputDialog.getText(None, title, message, qtw.QLineEdit.EchoMode.Normal, start_string)
    if ok:
        return text
    return None


class ColorButton(qtw.QPushButton):
    signalColorChanged = qtc.Signal(str)

    def __init__(self, hex):
        super().__init__()
        self.hx = hex
        self.setStyleSheet(f"background-color:{self.hx}")
        self.setText(self.hx)
        self.clicked.connect(self.color_pick)

    def color_pick(self):
        color_pick = qtw.QColorDialog.getColor(qtg.QColor(self.hx))
        if not color_pick.isValid():
            _logger.debug(f"Color invalid, cancel")
            return
        _logger.info(f"Color picked: {color_pick.name()}")
        if color_pick.isValid():
            r, g, b, a = color_pick.getRgb()
            self.hx = rgb_to_hex(r, g, b)
            self.setStyleSheet(f"background-color:{self.hx}")
            self.setText(self.hx)
            self.signalColorChanged.emit(self.hx)


class SettingsWidget(qtw.QWidget):
    signalSettingsChanged = qtc.Signal()
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
                _r = qtw.QWidget()
                _l = qtw.QHBoxLayout(_r)
                _l.setContentsMargins(0,0,0,0)
                _l.setSpacing(2)
                lb = qtw.QLabel(name)
                _l.addWidget(lb)
                lb.setSizePolicy(qtw.QSizePolicy.Policy.Fixed, qtw.QSizePolicy.Policy.Fixed)
                if _type != "button":
                    val = self.pd[key]
                if _type == "bool":
                    w = qtw.QCheckBox(name)
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
                if _type == "button":
                    lb.hide()
                    w = qtw.QPushButton(name)
                    w.pressed.connect(args[0])
                _l.addWidget(w)
                tgt_l.addWidget(_r)
        self._l.addStretch()

    def set(self, key, value):
        self.pd[key] = value
        self.signalSettingsChanged.emit()

    def __getitem__(self, key):
        return self.pd[key]
