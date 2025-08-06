class Feature():
    selectable = False
    movable = False
    stretchable = False
    rotatable = False
    stretch_fixed_ratio = False

    def edit(self):
        pass

    @property
    def bounding_box(self):
        raise NotImplementedError
        return (0, 0), (0, 0)

    @property
    def origin(self):
        raise NotImplementedError
        return (0, 0)

    def is_inside(self, x: float, y: float):
        return False