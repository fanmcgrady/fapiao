import os
import importlib
import numpy as np


from . import __vat_invoice_pipeline as base
importlib.reload(base)

from ..frame import textline
importlib.reload(textline)

from ..frame import _wireframe_template as wt
importlib.reload(wt)

from ..frame import wireframe
importlib.reload(wireframe)

from .. import config

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

        if 'textline_pars' in pars.keys():
            textline_pars = pars['textline_pars']
        else:
            textline_pars = dict(cuda=False)

        if textline_method == 'simple':
            thresh_pars = dict(mix_ratio=0.1, rows=4, cols=6, ksize=11, c=9)
            vat_invoice_pars = dict(thresh_pars=thresh_pars, char_expand_ratio=0.4)
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
        detect_wireframe = wireframe.Detect()

        # 线框匹配
        data = wt.WireframeTemplateData()
        data.load(config.WIREFRAME_TEMPLATE_VAT)
        match_wireframe = wt.WireframeTemplate(data=data, debug=debug)

        super(SpecialVatInvoicePipeline, self).__init__(detect_textlines,
                                                        classify_textlines, 
                                                        detect_wireframe,
                                                        match_wireframe,
                                                        debug)
