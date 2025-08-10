import os

from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

import threading
import logging

from common.constants import REMOTE
from common.ui import say
from redliner.common.constants import VERSION_PATTERN
from redliner.core.doc_man import DocMan
from redliner.common.common import resource_path

from redliner.common.temporary_file_manager import TemporaryFileManager
from redliner.common.persistent_dict import PersistentDict
from redliner.extensions.version_check import fetch_remote_version

VERSION = "x.x.x"

def get_version_number(changelog:str):
    for line in changelog.split("\n"):
        match = VERSION_PATTERN.search(line)
        if match:
            return match.group(1)

    return "0.0.0"

def parse_version_number(version:str) -> tuple:
    try:
        major, minor, revision = version.split(".")
        return (int(major), int(minor), int(revision))
    except:
        return (0,0,0)

with open(resource_path("CHANGELOG.md", None)) as f:
    VERSION = get_version_number(f.read())

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
        self.setCentralWidget(w)
        self.setAcceptDrops(True)
        self.show()
        self.signalParseUpdates.connect(self.parse_updates)

    def parse_updates(self, txt:str|Exception):
        remote_ver = get_version_number(txt)
        logging.info(f"Remote is version {remote_ver}")
        loc = parse_version_number(VERSION)
        remote = parse_version_number(remote_ver)
        for i in range(3):
            if remote[i] > loc[i]:
                say(f"There's a new version of Redliner! Local is {VERSION}, remote is {remote_ver}.\n\n{REMOTE}")
            if remote[i] < loc[i]:
                break

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.info("Start")
    with TemporaryFileManager() as tfm:
        app = qtw.QApplication(sys.argv)
        pd = PersistentDict(os.path.join(os.getenv('APPDATA'),"redliner","redliner.json"))
        _redliner = Redliner()
        file_check_thread =threading.Thread(target=lambda:fetch_remote_version(_redliner.signalParseUpdates.emit))
        qtc.QTimer.singleShot(1000, file_check_thread.start)
        try:
            pyi_splash.close()
        except:
            pass
        app.exec()
        file_check_thread.join()