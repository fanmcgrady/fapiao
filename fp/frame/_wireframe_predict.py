class WireframeRemap:
    def __init__(self, base_rect):
        self.base_rect = base_rect

    def to_relative(self, rect):
        bx, by, bw, bh = self.base_rect
        tx, ty, tw, th = rect
        return (tx - bx) / bw, (ty - by) / bh, tw / bw, th / bh

    def to_rect(self, relative):
        bx, by, bw, bh = self.base_rect
        rx, ry, rw, rh = relative
        return rx * bw + bx, ry * bh + by, rw * bw, rh * bh


class WireframeRelativeRect(object):

    def __init__(self):
        self.data = None

    def fit(self, files):
        pass

    def save(self, filename):
        pass

    def load(self, filename):
        return self.data
