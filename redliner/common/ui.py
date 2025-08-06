from PyQt6 import QtWidgets as qtw, QtCore as qtc
from .constants import PREVIEW_SIZE
from extensions.source_doc import SrcDoc

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

class DocPreview(qtw.QListWidget):
    signalSelectionChanged = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setUniformItemSizes(True)
        self.setIconSize(PREVIEW_SIZE)

    def set_doc(self, doc: SrcDoc):
        self.clear()
        for i in range(doc.page_count):
            qli = qtw.QListWidgetItem(str(i))
            qli.setTextAlignment(qtc.Qt.AlignmentFlag.AlignLeft)
            qli.setIcon(doc.preview(i))
            self.addItem(qli)

    def selectionChanged(self, selected, deselected):
        self.signalSelectionChanged.emit()
        return super().selectionChanged(selected, deselected)
