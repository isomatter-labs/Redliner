from PyQt6 import QtWidgets as qtw
from common import resource_path
import re


VERSION = "x.x.x"
version_pattern = re.compile(r'\[(\d+\.\d+\.\d+)\]')
with open(resource_path("CHANGELOG.md", None)) as f:
    for line in f:
        match = version_pattern.search(line)
        if match:
            VERSION = match.group(1)



class Redliner(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"Redliner v{VERSION}")
        self.resize(800, 600)
        self.show()

if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    _redliner = Redliner()
    app.exec()