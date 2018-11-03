import os
import importlib
import numpy as np

from . import __vat_invoice_pipeline as base

importlib.reload(base)

from ..frame import textline

importlib.reload(textline)

from ..frame import wireframe

importlib.reload(wireframe)

from .. import config

importlib.reload(config)

RELATIVE_TYPE = (0.11312122884218737,
                 -0.20238626390929312,
                 0.17701977509468628,
                 0.05366138923192387)

RELATIVE_SERIAL = (0.7508946029421918,
                   -0.2077524028324855,
                   0.15065512774015852,
                   0.05902752815511626)

RELATIVE_TITLE = (0.35542521805376187,
                  -0.25068018243005347,
                  0.28498886838859905,
                  0.06439355108123378)

RELATIVE_SURFACE = [-0.04412587, -0.32723426, 1.08490506, 1.47366346]
# x, y, w, h -> t, b, l, r
RELATIVE_HEAD = [0.3, -0.32, 0.4, 0.32]
RELATIVE_TAIL = [0.3, 1.00, 0.4, 0.32]


class SpecialVatInvoicePipeline(base._VatInvoicePipeline):
    def __init__(self, pars={}, debug=False):
        '''
        Args
            pars [dict]: for example, 
                dict(textline_method='simple')
                dict(textline_method='textboxes') (use deeplearning)
        '''
        # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）

        if 'textline_method' in pars.keys():
            textline_method = pars['textline_method']
        else:
            textline_method = 'simple'

        if textline_method == 'simple':
            thresh_pars = dict(mix_ratio=0.1, rows=4, cols=6, ksize=11, c=9)
            vat_invoice_pars = dict(std_image_size=(800, 512),
                                    thresh_pars=thresh_pars,
                                    char_expand_ratio=0.4,
                                    char_size_range=(5, 42, 5, 42))
            detect_textlines = textline.Detect(method='simple', pars=vat_invoice_pars, debug=debug)
        elif textline_method == 'textboxes':
            pars = dict(model_def=config.TEXTLINE_VAT_INVOICE_CAFFE['prototxt'],
                        model_weights=config.TEXTLINE_VAT_INVOICE_CAFFE['caffemodel'])
            detect_textlines = textline.Detect(method='textboxes', pars=pars, debug=debug)
        else:
            raise NotImplemented

        # 分类器
        classify_textlines = textline.Classify()

        # 线框检测器
        detect_wireframe = wireframe.Detect(debug=debug)

        # 发票到边界线框的相对比例
        extract_surface = wireframe.Extract(RELATIVE_SURFACE,
                                            RELATIVE_HEAD,
                                            RELATIVE_TAIL)

        # 线框匹配
        data = wireframe.WireframeTemplateData()
        data.load(config.WIREFRAME_TEMPLATE_VAT)
        match_wireframe = wireframe.WireframeTemplate(data=data, debug=debug)

        predict_pars = {'type': RELATIVE_TYPE,
                        'serial': RELATIVE_SERIAL,
                        'title': RELATIVE_TITLE}

        # SpecialVatInvoicePipeline, self
        super().__init__(detect_textlines,
                         classify_textlines,
                         detect_wireframe,
                         extract_surface,
                         match_wireframe,
                         predict_pars,
                         debug)
        self.invoice_type = 'special'
