import importlib
import numpy as np
import cv2

from ..core import quad

importlib.reload(quad)
from ..core import trans

importlib.reload(trans)
from ..core import line

importlib.reload(line)


class Find(object):
    '''find rects in image'''

    def __init__(self):
        self.approx_ratio = 0.02
        self.min_area = 60

    def __call__(self, mask):
        quads, conts = quad.find_quads(mask, approx_ratio=self.approx_ratio,
                                       min_area=self.min_area)
        if len(conts) == 0:
            return None, None
        boxes = [cv2.minAreaRect(cont) for cont in conts]
        areas = [box[1][0] * box[1][1] for box in boxes]
        idx = np.argmax(areas)
        return quads[idx], boxes[idx]


class Crop(object):
    def __init__(self, method=None, pars=None):
        pass

    def __call__(self, image, box):
        center, dsize, angle = box
        dsize = int(dsize[0]), int(dsize[1])
        return trans.rotate_crop(image, center, angle, dsize)


def _restore_box(box, fx):
    ifx = 1. / fx
    center, dsize, angle = box
    center = ifx * center[0], ifx * center[1]
    dsize = ifx * dsize[0], ifx * dsize[1]
    return center, dsize, angle


class Detect(object):
    def __init__(self):
        self.std_size = 400
        self.find_frame = Find()
        self.crop_frame = Crop()
        self.light = True

    def __call__(self, image):
        assert image is not None, 'Empty image'
        assert len(image.shape) == 3
        fx = 1. * self.std_size / np.min(image.shape[:2])
        im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im = cv2.resize(im, None, fx=fx, fy=fx)
        im = cv2.GaussianBlur(im, (3, 3), 1.2)
        if self.light:
            self.image = im
        max_pix = np.max(im)
        _, mask = cv2.threshold(im, max_pix - 2, 255, cv2.THRESH_BINARY_INV)
        if self.light:
            self.mask = mask
        quad, box = self.find_frame(mask)
        if box is None:
            return None
        box = _restore_box(box, fx)
        box_im = self.crop_frame(image, box)
        return box_im


class Adjust(object):
    def __init__(self):
        self.lsd = cv2.createLineSegmentDetector()
        self.th_ratio = 0.8

    def __call__(self, std_im):
        im = cv2.cvtColor(std_im, cv2.COLOR_BGR2GRAY)
        lines0 = self._detect_region(im[:40, :])
        lines1 = self._detect_region(im[-40:, :])
        lines = np.concatenate((lines0, lines1))

        line_lens_th = np.max(list(map(line.line_length, lines))) * self.th_ratio
        strong_lines = list(filter(lambda x: line.line_length(x) > line_lens_th, lines))
        line_angs = np.array(list(map(line.line_angle, strong_lines)))
        line_lens = np.array(list(map(line.line_length, strong_lines)))
        ang = np.sum(line_angs * line_lens) / np.sum(line_lens)
        h, w = std_im.shape[:2]
        im_ft = trans.rotate_crop(std_im, center=(w / 2, h / 2), angle=ang, dsize=(w, h),
                                  border_color=(255, 255, 255))
        return im_ft

    def _detect_region(self, sub_im):
        _lines, width, prec, nfa = self.lsd.detect(sub_im)
        _lines = np.squeeze(_lines)
        return _lines
