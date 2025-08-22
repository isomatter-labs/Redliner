import logging
from PyQt6 import QtWidgets as qtw, QtCore as qtc
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from redliner.common.constants import PREVIEW_SIZE
from redliner.extensions.source_doc import SrcDoc
from pathlib import Path

_logger = logging.getLogger(__name__)

class DocPreview(qtw.QListWidget):
    signalSelectionChanged = qtc.pyqtSignal()
    signalFileDropRequest = qtc.pyqtSignal(Path)

    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        self.setUniformItemSizes(True)
        self.setIconSize(PREVIEW_SIZE)

        # Enable drag and drop so we can parse new files that have been dropped onto the DocPreview
        self.setAcceptDrops(True)

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

    def keyPressEvent(self, e):
        if e.key() in [qtc.Qt.Key.Key_Escape, qtc.Qt.Key.Key_PageUp, qtc.Qt.Key.Key_PageDown, qtc.Qt.Key.Key_Home]:
            self.parent.keyPressEvent(e)
        else:
            super().keyPressEvent(e)

    @staticmethod
    def _urlFromEvent(event: QDragEnterEvent | QDropEvent) -> qtc.QUrl | None:
        if event.mimeData().hasUrls(): # type: ignore[union-attr]
            urls = event.mimeData().urls() # type: ignore[union-attr]
            if len(urls) == 1:
                return urls[0].toLocalFile() # type: ignore[union-attr]
        return None

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        # NOTE: Enter event must be accepted before dragEvent is triggered!
        url = self._urlFromEvent(event)
        _logger.debug(f"Dragged file entered: {url}")
        # Check if the URL is a file path
        if url and Path(url).is_file():
            # TODO: Handle file type-checking to indicate to the user certain files can't be diffed. I think this
            # requires a bit of a rethink for how valid files are deteced in Fetcher, so keep it simple for now
            _logger.debug(f"File allowed: {url}")
            event.acceptProposedAction() # type: ignore[union-attr]
        else:
            _logger.debug(f"File rejected: {url}")
            event.ignore() # type: ignore[union-attr]

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        # NOTE: Drag event must be accepted before dropEvent is triggered! It should already be verified so we can just
        # accept.
        event.acceptProposedAction() 


    def dropEvent(self, event: QDropEvent) -> None:
        url = self._urlFromEvent(event)
        if url and Path(url).is_file():
            _logger.info(f"Dragged file dropped: {url}")
            self.signalFileDropRequest.emit(Path(url))
            event.acceptProposedAction() # type: ignore[union-attr]
        else:   
            event.ignore() # type: ignore[union-attr]