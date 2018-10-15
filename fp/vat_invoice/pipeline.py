import importlib

from . import _special_vat_invoice

importlib.reload(_special_vat_invoice)
from ._special_vat_invoice import SpecialVatInvoicePipeline


class VatInvoicePipeline(object):
    def __init__(self, invoice_type, pars={}, debug=False):
        '''
        Args
            invoice_type [str], can be
                'special'
                'electric'
            pars [dict]: for example, 
                dict(textline_method='simple')
                dict(textline_method='textboxes') (use deeplearning)
        '''
        if invoice_type == 'special':
            self.pipe = SpecialVatInvoicePipeline(pars=pars, debug=debug)
        else:
            raise NotImplemented

    def __call__(self, image):
        res = self.pipe(image)
        self.__dict__.update(vars(self.pipe))

    def roi_textlines(self, roi_name):
        '''pipe.roi_textlines(roi_name) -> list of rects
        Args
            roi_name [str] support,
                'general', the genereal wireframe,
                'header0', left part of header, containing invoice type,
                'header1', center part of header, containing invoice title,
                'header2', right part of header, containing invoice serial and time,
                'buyer', rect for buyer,
                'tax_free', rect for tax_free price
                'money', rect for money (chinese and digital),
                'saler', rect for saler
        Return
          a list of textline rects, which is inside of specified ROI
        '''
        return self.pipe.roi_textlines(roi_name)

    def predict(self, textline_name):
        '''pipe.predict(textline_name) -> rect
        Args
            textline_name [str] support 
                'type'： invoice type
                'title': invoice title
                'serial': invoice serial number
                'time': time to made invoice
                'tax_free_money': money without tax
        Return
          a textline rect (x, y, w, h)
        '''
        return self.pipe.predict(textline_name)
