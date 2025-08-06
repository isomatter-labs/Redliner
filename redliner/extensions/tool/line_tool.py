from PyQt6 import QtCore as qtc, QtGui as qtg
from . import Tool
from ..feature.infinite_crosshair_feature import InfiniteCrosshairFeature

class LineTool(Tool):
    name = "Line"

    # def update(self, mouse_buffer: list[tuple], features: list, sources: list[qtg.QImage], modifiers: qtc.Qt.KeyboardModifier):
    #     if len(mouse_buffer) == 1:
    #         new_features = [InfiniteCrosshairFeature()]
    #     return finished, features, preview_features

    def cancel(self):
        pass