# utf-8
import os
import importlib
import numpy as np
import cv2

from .. import config

importlib.reload(config)
from ..util import check

importlib.reload(check)

from ..frame import surface, textline, template

importlib.reload(surface)
importlib.reload(textline)
importlib.reload(template)

from . import train_ticket

importlib.reload(train_ticket)

from . import __train_ticket_pipeline as pipeline

importlib.reload(pipeline)


class ExcessTrainTicketPipeline(pipeline._TrainTicketPipeline):
    '''
    '''

    def __init__(self, debug=False):
        # 创建 发票票面 检测器 （无需再使用 Adjust 类）
        detect_surface = surface.Detect(debug=debug)
        # 检查是否上下颠倒火车票
        check_upside_down = train_ticket.UpsideDownCheck_v2()

        # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）
        thresh_pars = dict(mix_ratio=0.1, rows=1, cols=3, ksize=11, c=9)
        train_ticket_pars = dict(thresh_pars=thresh_pars, char_expand_ratio=0.5)
        detect_textlines = textline.Detect(pars=train_ticket_pars,
                                           debug=debug)

        # 创建模板匹配器
        init_yaml = config.TEMPLATE_TRAIN_TICKET_EXCESS
        match_template = template.Template(init_yaml=init_yaml,
                                           warp_method='translate',
                                           learning_rate=0.1,
                                           debug=debug)

        super(ExcessTrainTicketPipeline, self).__init__(detect_surface,
                                                        check_upside_down,
                                                        detect_textlines,
                                                        match_template,
                                                        debug)

        self.debug = dict() if debug else None
