import importlib
import numpy as np
import cv2


def line_point(p0, p1, r):
    assert isinstance(p0, np.ndarray)
    assert isinstance(p1, np.ndarray)
    return p0 + (p1 - p0) * r


class RelativeBoxPoints(object):
    ''' Input a rotated box, output relative rects
    '''

    def __init__(self, relative_rect):
        rx, ry, rw, rh = relative_rect
        self.extend_pars = ry, ry + rh, rx, rx + rw  # top, bottom, left, right

    def __call__(self, wireframe_box):
        box = wireframe_box
        assert len(box) == 3 and len(box[0]) == len(box[1]) == 2
        src_points = cv2.boxPoints(box)
        rt, rb, rl, rr = self.extend_pars
        p0, p1, p2, p3 = src_points

        p0a = line_point(p1, p0, rb)
        p1a = line_point(p1, p0, rt)
        p2a = line_point(p2, p3, rt)
        p3a = line_point(p2, p3, rb)

        # return np.array([p0a, p1a, p2a, p3a])
        p0b = line_point(p0a, p3a, rl)
        p1b = line_point(p1a, p2a, rl)
        p2b = line_point(p1a, p2a, rr)
        p3b = line_point(p0a, p3a, rr)

        dst_points = np.array([p0b, p1b, p2b, p3b])
        return dst_points

    def rectr(self, surface_size):
        return None
