from PyQt6 import QtCore as qtc

class Tool():
    name = "Abstract Tool"

    def update(self, mouse_buffer: list[tuple], features: list, sources: list[qtg.QImage],
               modifiers: qtc.Qt.KeyboardModifier):
        """

        """
        raise NotImplementedError
        return finished, features, preview_features

    def cancel(self, ):
        pass