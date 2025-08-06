from . import Feature

class LineFeature(Feature):
    def __init__(self, mouse_buffer:list[tuple], features:list, sources:list[qtg.QImage], modifiers:qtc.Qt.KeyboardModifier):
        self.x1, self.y1 = mouse_buffer[0]
        self.x2, self.y2 = mouse_buffer[1]
        pass

    def delete(self):
        raise NotImplementedError

    def edit(self):
        pass

    def render(self):
        raise NotImplementedError

    @property
    def bounding_box(self):
        raise NotImplementedError
        return (0,0), (0,0)