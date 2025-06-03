from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc
from common import resource_path
import re


VERSION = "x.x.x"
version_pattern = re.compile(r'\[(\d+\.\d+\.\d+)\]')
with open(resource_path("CHANGELOG.md", None)) as f:
    for line in f:
        match = version_pattern.search(line)
        if match:
            VERSION = match.group(1)


try:
    import pyi_splash
    pyi_splash.update_text("Done extracting, starting program...")
except:
    pass  # This is only used when compiling to .exe

class RenderWidget(qtw.QLabel):
    signalClick = qtc.pyqtSignal(float, float, qtc.Qt.MouseButton) # canvas X,Y
    signalDrag = qtc.pyqtSignal(float, float)
    signalRelease = qtc.pyqtSignal(float, float, qtc.Qt.MouseButton)
    signalKeyPressed = qtc.pyqtSignal
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image:qtg.QImage|None = None
        self.x = 0 # pixels, top-left is center
        self.y = 0
        self.angle = 0 # degrees
        self.scale = 1

    def mousePressEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        self.signalClick.emit(x, y, ev.button())

    def mouseMoveEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        self.signalDrag.emit(x, y)
        
    def mouseReleaseEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        self.signalRelease.emit(x, y, ev.button())
    
    def cursor_pos_to_canvas_pos(x:float, y:float):
        ...
    
    def redraw():
        self.


class Redliner(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"Redliner v{VERSION}")
        self.resize(800, 600)
        self.setWindowIcon(qtg.QIcon(resource_path('icon.png')))

        r = RenderWidget()

        self.setCentralWidget(r)
        self.setAcceptDrops(True)
        self.show()

if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    _redliner = Redliner()
    try:
        pyi_splash.close()
    except:
        pass
    app.exec()