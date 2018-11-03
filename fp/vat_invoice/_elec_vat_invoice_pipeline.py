import os
import importlib
import numpy as np
import cv2
import torch
import torchvision

from . import __vat_invoice_pipeline as base

importlib.reload(base)

from ..frame import textline

importlib.reload(textline)

from ..frame import wireframe

importlib.reload(wireframe)

from ..frame import table

importlib.reload(table)

from .. import config

importlib.reload(config)

from ..util import visualize

importlib.reload(visualize)

RELATIVE_TITLE = [0.30033048, -0.23306587, 0.39122961, 0.09269564]
RELATIVE_TYPE = [0.7891041, -0.2317254, 0.11356049, 0.04723731]
RELATIVE_SERIAL = [0.78951921, -0.1755754, 0.07695353, 0.04545476]
RELATIVE_TIME = [0.78785618, -0.12566191, 0.11771833, 0.04990635]
RELATIVE_VERIFY = [0.79076765, -0.07219048, 0.19550675, 0.04901985]
RELATIVE_SURFACE = [-0.04412587, -0.32723426, 1.08490506, 1.47366346]
RELATIVE_HEAD = [0.0, -0.32, 1.0, 0.32]
RELATIVE_TAIL = [0.0, 1.00, 1.0, 0.32]


class ElecVatInvoicePipeline(base._VatInvoicePipeline):
    def __init__(self, pars={}, debug=False):
        if 'textline_method' in pars.keys():
            textline_method = pars['textline_method']
        else:
            textline_method = 'simple'

        if textline_method == 'simple':
            thresh_pars = dict(mix_ratio=0.1, rows=4, cols=6, ksize=11, c=9)
            vat_invoice_pars = dict(std_image_size=(800, 512),
                                    thresh_pars=thresh_pars,
                                    char_expand_ratio=0.2,
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
        match_wireframe = wireframe.WireframeTemplate(data=data, header_fx=0.295, debug=debug)

        predict_pars = {'type': RELATIVE_TYPE,
                        'serial': RELATIVE_SERIAL,
                        'title': RELATIVE_TITLE,
                        'time': RELATIVE_TIME,
                        'verify': RELATIVE_VERIFY}

        super().__init__(detect_textlines,
                         classify_textlines,
                         detect_wireframe,
                         extract_surface,
                         match_wireframe,
                         predict_pars,
                         debug)
        self.invoice_type = 'elec'

        self.debug = dict() if debug else None

    def _predict_type(self):
        textlines = self.roi_textlines('header2')
        rows = table.TableParser()(textlines)
        return rows[3] if len(rows) == 4 else self._predict('type')

    def _predict_serial(self):
        textlines = self.roi_textlines('header2')
        rows = table.TableParser()(textlines)
        return rows[2] if len(rows) == 4 else self._predict('serial')

    def _predict_time(self):
        textlines = self.roi_textlines('header2')
        rows = table.TableParser()(textlines)
        return rows[1] if len(rows) == 4 else None

    def _predict_verify(self):
        textlines = self.roi_textlines('header2')
        rows = table.TableParser()(textlines)
        return rows[0] if len(rows) == 4 else self._predict('verify')
