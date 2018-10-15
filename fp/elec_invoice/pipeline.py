import os
import importlib
import numpy as np
import cv2

from ..frame import _wireframe_template as wt

importlib.reload(wt)

from ..frame import wireframe

importlib.reload(wireframe)

from .. import config

importlib.reload(config)

from ..util import visualize

importlib.reload(visualize)


class ElecInvoicePipeline(object):
    def __init__(self, pars={}, debug=False):
        # 线框检测器
        detect_wireframe = wireframe.Detect()

        # 线框匹配
        data = wt.WireframeTemplateData()
        data.load(config.WIREFRAME_TEMPLATE_VAT)
        match_wireframe = wt.WireframeTemplate(data=data, debug=debug)

        self.detect_wireframe = detect_wireframe
        self.match_wireframe = match_wireframe

        self.debug = dict() if debug else None

    def __call__(self, image):

        gray_surface_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        frame_points = self.detect_wireframe(gray_surface_image)  # , frame_rects

        if self.match_wireframe is None:
            self.exit_msg = 'Null wireframe matcher'
            return False

        frame_points = np.array(frame_points, dtype=np.float32)
        if self.debug is not None:
            self.debug['points'] = visualize.points(gray_surface_image,
                                                    frame_points,
                                                    radius=3)

        # rectr = self.match_wireframe(frame_points, image_size)
        # W, H = image_size
        # xr, yr, wr, hr = rectr
        # self.roi['general'] = (xr*W).item(), (yr*H).item(), (wr*W).item(), (hr*H).item()
        # self.roi['buyer'] = self.match_wireframe.roi(image_size, 0, 1)
