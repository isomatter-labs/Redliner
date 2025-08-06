from PyQt6 import QtWidgets as qtw

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
