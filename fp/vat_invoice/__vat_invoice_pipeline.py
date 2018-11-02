import importlib
import numpy as np
import cv2

from ..core import rectangle, trans

importlib.reload(rectangle)
importlib.reload(trans)
from ..util import check

importlib.reload(check)
from ..util import visualize

importlib.reload(visualize)

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
                 detect_wireframe, extract_surface, match_wireframe,
                 predict_pars,
                 debug=False):
        self.detect_textlines = detect_textlines
        self.classify_textlines = classify_textlines
        self.detect_wireframe = detect_wireframe
        self.extract_surface = extract_surface
        self.match_wireframe = match_wireframe
        self.predict_pars = predict_pars
        self.reset()
        self.invoice_type = None
        self.inter_ratio_min = 0.2
        self.debug = dict() if debug else None

    def __call__(self, image, no_background=True):
        assert check.valid_image(image, colored=1)
        self.reset()

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #########
        # deskew
        #########
        assert self.detect_wireframe is not None
        assert self.extract_surface is not None
        assert self.match_wireframe is not None

        if self.debug is not None:
            print('[1/5]\nDetect surface box... ')

        _, wireframe_box, _ = self.detect_wireframe(gray_image)
        center, (size0, size1), angle = wireframe_box
        if size0 < size1:
            wireframe_box = center, (size1, size0), angle + 90.
        if self.debug is not None:
            self.debug['wireframe_box'] = wireframe_box
            self.debug['wireframe_box_show'] = visualize.box(image, wireframe_box)
            print('Done.')
            print('* wirframe_box:')
            print('  (({:.2f}, {:.2f}), ({:.2f}, {:.2f}), {:.2f}) '.format(center[0],
                                                                           center[1],
                                                                           wireframe_box[1][0],
                                                                           wireframe_box[1][1],
                                                                           wireframe_box[2]))
            print('[2/5]\nExtract surface image... ')

        surface_points, surface_image = self.extract_surface(image, wireframe_box)
        gray_surface_image = cv2.cvtColor(surface_image, cv2.COLOR_BGR2GRAY)
        image_size = surface_image.shape[1], surface_image.shape[0]
        self.wireframe_box = wireframe_box
        self.surface_image = surface_image

        if self.debug is not None:
            print('Done.')
            print('* surface_points:\n', surface_points)
            print('* surface_image.shape: ', surface_image.shape)
            print('[3/5]\nDetect wirframe...')
        # get rois
        frame_points, _, init_rectr = self.detect_wireframe(gray_surface_image)
        # print('finish detect points')
        frame_points = np.array(frame_points, dtype=np.float32)
        rectr = self.match_wireframe(frame_points, image_size, init_rectr)
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

        ############
        # TEXTLINES
        ############
        if self.debug is not None:
            print('Done.')
            print('[4/5]\nDetect textlines...')
            
        if self.detect_textlines is None:
            self.exit_msg = 'Null textlines detector'
            if self.debug is not None:
                print(self.exit_msg)
            return False

        if self.detect_textlines.method == 'simple':
            input_image = gray_surface_image
        elif self.detect_textlines.method == 'textboxes':
            input_image = surface_image
        else:
            raise NotImplemented
        detected_rects = self.detect_textlines(input_image)
        if detected_rects is None or len(detected_rects) == 0:
            self.exit_msg = 'Detected zero textlines'
            return False
        assert check.valid_rects(detected_rects, strict=True)
        #for rect_ in detected_rects:
        #    assert rect_[2] > 0 and rect_[3] > 0
        self.textlines = np.array(detected_rects)

        if self.debug is not None:
            print('Done.')
            print('[5/5]\nClassify textlines...')
        
        if self.classify_textlines is None:
            self.exit_msg = 'Null textlines classifier.'
            if self.debug is not None:
                print(self.exit_msg)
            return False
        detected_types = self.classify_textlines(gray_surface_image, 
                                                 detected_rects)
        self.textlines_type = detected_types

        if self.debug is not None:
            self.debug['result'] = self._draw_result(surface_image)
            print('Done. END.')

        return True
        
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
        predict_ = {'type': self._predict_type,
                    'serial': self._predict_serial,
                    'title': self._predict_title,
                    'time': self._predict_time,
                    'verify': self._predict_verify,
                    'tax_free_money': self._predict_tax_free}

        assert textline_name in predict_.keys()
        return predict_[textline_name]()

    def _predict(self, textline_name, detect_revise=True):
        if textline_name not in self.predict_pars.keys():
            return None
        rect = relative_to_rect(self.predict_pars[textline_name], self.roi['general'])
        if detect_revise == False:
            return rect
        ious = [rectangle.iou(rect, r) for r in self.textlines]
        best_match_i = np.argmax(ious)
        if ious[best_match_i] > 0.5:
            return self.textlines[best_match_i]
        else:
            return rect

    def _predict_type(self):
        return self._predict('type')

    def _predict_serial(self):
        return self._predict('serial')

    def _predict_title(self):
        return self._predict('title', detect_revise=False)

    def _predict_time(self):
        # TODO
        if 'time' not in self.predict_pars.keys():
            rects = self.roi_textlines('header2')
            rects = np.array([rect for rect in rects if rect[2] > 4.0 * rect[3]])
            if len(rects) == 0:
                return None
            time_idx = np.argmax([0.3 * (rect[0] + rect[2]) + 0.7 * (rect[1] + rect[3]) for rect in rects])
            return rects[time_idx]
        else:
            return self._predict('time')

    def _predict_verify(self):
        return self._predict('verify')

    def _predict_tax_free(self):
        rects = self.roi_textlines('tax_free')
        if len(rects) == 0:
            return None
        time_idx = np.argmax([rect[1] for rect in rects])
        return rects[time_idx]
        
    def _draw_result(self, image):
        image = image.copy()

        for key in self.roi.keys():
            x, y, w, h = self.roi[key]
            x, y, w, h = int(x), int(y), int(w), int(h)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), thickness=2)
            
        image = visualize.rects(image, self.textlines, self.textlines_type)

        keys = {'special': ['type', 'serial', 'title', 'time', 'tax_free_money'],
                'normal': ['type', 'serial', 'title', 'time', 'tax_free_money', 'verify'],
                'elec': ['type', 'serial', 'title', 'time', 'tax_free_money', 'verify'], }
        assert self.invoice_type is not None
        for key in keys[self.invoice_type]:
            _rect = self.predict(key)
            if _rect is None:
                continue
            x, y, w, h = _rect
            x, y, w, h = int(x), int(y), int(w), int(h)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), thickness=4)
        
        return image
