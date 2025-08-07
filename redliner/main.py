import os

from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

import threading
import logging

from redliner.common.constants import VERSION_PATTERN
from redliner.core.doc_man import DocMan
from redliner.common.common import resource_path

from redliner.common.temporary_file_manager import TemporaryFileManager
from redliner.common.persistent_dict import PersistentDict
from redliner.extensions.version_check import fetch_remote_version

VERSION = "x.x.x"
with open(resource_path("CHANGELOG.md", None)) as f:
    for line in f:
        match = VERSION_PATTERN.search(line)
        if match:
            VERSION = match.group(1)

try:
    import pyi_splash
    pyi_splash.update_text("Done extracting, starting program...")
except:
    pass  # This is only used when compiling to .exe


class Redliner(qtw.QMainWindow):
    signalParseUpdates = qtc.pyqtSignal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"Redliner v{VERSION}")
        self.resize(800, 600)
        self.setWindowIcon(qtg.QIcon(resource_path('icon.png')))

        w = DocMan()
        _l = qtw.QHBoxLayout(w)
        self.setCentralWidget(w)
        self.setAcceptDrops(True)
        self.show()
        self.signalParseUpdates.connect(self.parse_updates)

    def parse_updates(self, txt:str|Exception):
        # TODO: implement new version notification
        logging.info(str(txt))

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.info("Start")
    with TemporaryFileManager() as tfm:
        app = qtw.QApplication(sys.argv)
        pd = PersistentDict(os.path.join(os.getenv('APPDATA'),"redliner","redliner.json"))
        _redliner = Redliner()
        file_check_thread =threading.Thread(target=lambda:fetch_remote_version(_redliner.signalParseUpdates.emit))
        qtc.QTimer.singleShot(1, file_check_thread.start)
        try:
            pyi_splash.close()
        except:
            pass
        app.exec()
        file_check_thread.join()