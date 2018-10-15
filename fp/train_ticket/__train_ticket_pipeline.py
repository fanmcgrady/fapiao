# utf-8
import os
import importlib
import numpy as np
import cv2

from ..util import check

importlib.reload(check)
from ..core import trans

importlib.reload(trans)

from . import train_ticket

importlib.reload(train_ticket)


class _TrainTicketPipeline(object):
    '''
    textline extraction and template match for blue train ticket
    '''

    def __init__(self, detect_surface, is_upside_down,
                 detect_textlines, match_template, debug=False):
        '''
        Args:
          debug : for debuging only
        '''
        self.reset()

        # 创建 发票票面 检测器 （无需再使用 Adjust 类）
        self.detect_surface = detect_surface
        # 检查是否上下颠倒火车票
        self.check_upside_down = is_upside_down

        # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）
        self.detect_textlines = detect_textlines

        # 创建模板匹配器
        self.match_template = match_template

        self.debug = dict() if debug else None

    def reset(self):
        self.is_blue = None
        self.surface_image = None
        self.textlines = None
        self.template = None
        self.guess = None
        self.exit_msg = None

    def __call__(self, image, no_background=False):
        '''
        Args:
          image : input color image
          no_background : set to True if no background in input image
        '''
        assert check.valid_image(image, colored=1)
        self.reset()

        if not no_background:
            # 检测提取
            surface_image = self.detect_surface(image)
            if surface_image is None:
                self.exit_msg = 'Detected zero ticket'
                return False
        else:
            if image.shape[0] < image.shape[1]:
                surface_image = image
            else:
                surface_image = trans.rotate90(image)

        # 检查是否蓝色票
        self.is_blue = train_ticket.is_blue(surface_image)
        # 是否上下颠倒，是则旋转180°
        if self.check_upside_down(surface_image):
            surface_image = trans.rotate180(surface_image)
        self.surface_image = surface_image

        gray_surface_image = cv2.cvtColor(surface_image, cv2.COLOR_BGR2GRAY)
        std_size = surface_image.shape[1], surface_image.shape[0]

        detected_rects = self.detect_textlines(gray_surface_image)
        self.textlines = detected_rects
        if len(detected_rects) == 0:
            self.exit_msg = 'Detected zero textlines'
            return False

        # 匹配模板
        if self.match_template is None:
            return True
        new_named_rects, succeed = self.match_template(detected_rects=detected_rects,
                                                       image_size=std_size,  # image size of detection
                                                       para_init=None, update=False)
        self.template = new_named_rects
        self.guess = [self.match_template.data.keys[j] for j, i in enumerate(succeed) if i == 0]

        return True
