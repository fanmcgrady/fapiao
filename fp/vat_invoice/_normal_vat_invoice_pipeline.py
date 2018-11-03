import os
import importlib
import numpy as np

from . import _special_vat_invoice_pipeline as base

importlib.reload(base)

from ..frame import textline

importlib.reload(textline)

from ..frame import wireframe

importlib.reload(wireframe)

from .. import config

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


class NormalVatInvoicePipeline(base.SpecialVatInvoicePipeline):
    def __init__(self, pars={}, debug=False):
        '''
        Args
            pars [dict]: for example, 
                dict(textline_method='simple')
                dict(textline_method='textboxes') (use deeplearning)
        '''
        super(NormalVatInvoicePipeline, self).__init__(pars=pars, debug=debug)
        self.invoice_type = 'normal'

    def _predict_verify(self):
        return 0, 0, 0, 0
