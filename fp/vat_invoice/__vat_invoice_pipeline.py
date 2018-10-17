import importlib
import numpy as np
import cv2

from ..core import rectangle
from ..util import check
from ..util import visualize

def relative_to_rect(relative_ratio, general_rect):
    x, y, w, h = general_rect
    rx, ry, rw, rh = relative_ratio
    dx = rx * w + x
    dy = ry * h + y
    dw = rw * w
    dh = rh * h
    return dx, dy, dw, dh

class _VatInvoicePipeline(object):
    def __init__(self, detect_textlines, classify_textlines,
                 detect_wireframe, match_wireframe, debug=False):
        self.detect_textlines = detect_textlines
        self.classify_textlines = classify_textlines
        self.detect_wireframe = detect_wireframe
        self.match_wireframe = match_wireframe
        self.reset()
        self.inter_ratio_min = 0.2
        self.debug = dict() if debug else None

    def __call__(self, image, no_background=True):
        assert check.valid_image(image, colored=1)
        self.reset()

        surface_image = image
        image_size = surface_image.shape[1], surface_image.shape[0]
        gray_surface_image = cv2.cvtColor(surface_image, cv2.COLOR_BGR2GRAY)

        if self.detect_textlines is None:
            self.exit_msg = 'Null textlines detector'
            return False

        if self.detect_textlines.method == 'simple':
            input_image = gray_surface_image
        elif self.detect_textlines.method == 'textboxes':
            input_image = surface_image
        else:
            raise NotImplemented
        detected_rects = self.detect_textlines(input_image)
        if len(detected_rects) == 0:
            self.exit_msg = 'Detected zero textlines'
            return False
        assert check.valid_rects(detected_rects, strict=True)
        # for rect_ in detected_rects:
        #    assert rect_[2] > 0 and rect_[3] > 0
        self.textlines = detected_rects

        if self.classify_textlines is None:
            self.exit_msg = 'Null textlines classifier.'
            return False
        detected_types = self.classify_textlines(gray_surface_image, 
                                                 detected_rects)
        self.textlines_type = detected_types

        if self.detect_wireframe is None:
            self.exit_msg = 'Null wireframe detector.'
            return False

        frame_points = self.detect_wireframe(gray_surface_image)  # , frame_rects
        
        if self.match_wireframe is None:
            self.exit_msg = 'Null wireframe matcher'
            return False

        frame_points = np.array(frame_points, dtype=np.float32)
        rectr = self.match_wireframe(frame_points, image_size)
        W, H = image_size
        xr, yr, wr, hr = rectr
        self.roi['general'] = (xr * W).item(), (yr * H).item(), (wr * W).item(), (hr * H).item()
        self.roi['buyer'] = self.match_wireframe.roi(image_size, 0, 1)
        self.roi['tax_free'] = self.match_wireframe.roi(image_size, 1, 5)  # net price, tax-free
        self.roi['money'] = self.match_wireframe.roi(image_size, 2, 1)
        self.roi['saler'] = self.match_wireframe.roi(image_size, 3, 1)
        self.roi['header0'] = self.match_wireframe.roi(image_size, -1, 0)
        self.roi['header1'] = self.match_wireframe.roi(image_size, -1, 1)
        self.roi['header2'] = self.match_wireframe.roi(image_size, -1, 2)

        if self.debug is not None:
            self.debug['result'] = self._draw_result(surface_image)

    def reset(self):
        self.textlines = None
        self.textlines_type = None
        self.rectr = None
        self.roi = dict()

    def roi_textlines(self, roi_name):
        assert roi_name in self.roi.keys()

        _textlines = []
        for textline in self.textlines:
            rect_inter = rectangle.intersect(textline, self.roi[roi_name])
            if rect_inter[2] <= 0 or rect_inter[3] <= 0:
                continue
            area_inter = rect_inter[2] * rect_inter[3]
            area_textline = textline[2] * textline[3]
            if area_inter / area_textline > self.inter_ratio_min:
                _textlines.append(textline)

        return np.array(_textlines)

    def predict(self, textline_name):
        '''
        Arg
            textline_name [str] support:
                'type'
                'serial'
                'title'
                'time'
                'tax_free_money'
        '''
        type_rel_ratio = (0.11312122884218737,
                          -0.20238626390929312,
                          0.17701977509468628,
                          0.05366138923192387)

        serial_rel_ratio = (0.7508946029421918,
                            -0.2077524028324855,
                            0.15065512774015852,
                            0.05902752815511626)

        title_rel_ratio = (0.35542521805376187,
                           -0.25068018243005347,
                           0.28498886838859905,
                           0.06439355108123378)

        if textline_name == 'type':
            return relative_to_rect(type_rel_ratio, self.roi['general'])
        elif textline_name == 'serial':
            return relative_to_rect(serial_rel_ratio, self.roi['general'])
        elif textline_name == 'title':
            return relative_to_rect(title_rel_ratio, self.roi['general'])

        elif textline_name == 'time':
            rects = self.roi_textlines('header2')
            if len(rects) == 0:
                return None
            time_idx = np.argmax([rect[0] + rect[1] for rect in rects])
            return rects[time_idx]
        elif textline_name == 'tax_free_money':
            rects = self.roi_textlines('tax_free')
            if len(rects) == 0:
                return None
            time_idx = np.argmax([rect[1] for rect in rects])
            return rects[time_idx]
        else:
            raise NotImplemented

    def _draw_result(self, image):
        image = image.copy()

        for key in self.roi.keys():
            x, y, w, h = self.roi[key]
            x, y, w, h = int(x), int(y), int(w), int(h)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), thickness=2)
            
        image = visualize.rects(image, self.textlines, self.textlines_type)

        for key in ['type', 'title', 'serial', 'time', 'tax_free_money']:
            x, y, w, h = self.predict(key)
            x, y, w, h = int(x), int(y), int(w), int(h)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), thickness=4)
        
        return image
