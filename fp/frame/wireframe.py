import importlib
import numpy as np
import cv2
import matplotlib.pyplot as pl

from ..core import trans

importlib.reload(trans)

from . import _wireframe_corner

importlib.reload(_wireframe_corner)
from ._wireframe_corner import LineSegDetect, CornerPointDetect

from . import _wireframe_prelocate

importlib.reload(_wireframe_prelocate)
from ._wireframe_prelocate import PreLocateWireframe as Prelocate

from ..frame import _surface_extract

importlib.reload(_surface_extract)
from ._surface_extract import RelativeBoxPoints

from . import _wireframe_template

importlib.reload(_wireframe_template)
from ._wireframe_template import WireframeTemplateData, WireframeTemplate
            
class Detect(object):
    def __init__(self, debug=False):
        self.detect_lines = LineSegDetect(debug=debug)
        self.detect_corners = CornerPointDetect()
        self.prelocate = Prelocate(debug=debug)
        
    def __call__(self, image):
        '''
        output box'''
        # print('     Wirframe.Detect begin')
        lines = self.detect_lines(image)
        #print('     Wirframe.Detect.lines done')
        points, lineids = self.detect_corners(lines)
        # print('     Wirframe.Detect.points done')
        image_size = image.shape[1], image.shape[0]
        box, init_rectr = self.prelocate(points, image_size)
        # print('     Wirframe.Detect.box done')
        return points, box, init_rectr
    
def visualize(image, points):
    imx = cv2.merge((image, image, image))
    for x, y in points:
        x = int(round(x))
        y = int(round(y))
        cv2.circle(imx, (x, y), 3, (255, 0, 0), thickness=1)
    return imx


class Extract(object):
    def __init__(self, relative_surface, relative_head, relative_tail):
        self.extract_surface = RelativeBoxPoints(relative_surface)
        self.extract_head = RelativeBoxPoints(relative_head)
        self.extract_tail = RelativeBoxPoints(relative_tail)

    def __call__(self, image, wireframe_box):
        '''
        output a standard image
        '''
        head_pix = self._pixel_mean(self.extract_head, image, wireframe_box)
        tail_pix = self._pixel_mean(self.extract_tail, image, wireframe_box)
        print('head_pix', head_pix)
        print('tail_pix', tail_pix)
        if head_pix > tail_pix:
            wireframe_box = wireframe_box[0], wireframe_box[1], wireframe_box[2] + 180.
        surface_points = self.extract_surface(wireframe_box)
        surface_image = trans.deskew(image, surface_points)
        return surface_points, surface_image

    def _pixel_mean(self, points_func, image, box):
        _points = points_func(box)
        _image = trans.deskew(image, _points)
        # unlock this to test
        # pl.figure()
        # pl.imshow(_image)
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
        _, _image = cv2.threshold(_image, 20, 255, cv2.THRESH_OTSU)
        return np.mean(_image)
