import fp


# 初始化pipeline，提高加载速度
class PipelineInit(object):
    def __init__(self):
        print("init special pipe")
        self.special_pipe = fp.vat_invoice.pipeline.VatInvoicePipeline('special',
                                                                       pars=dict(textline_method='textboxes'),
                                                                       debug=False)
        print("init normal pipe")
        self.normal_pipe = fp.vat_invoice.pipeline.VatInvoicePipeline('normal', pars=dict(textline_method='textboxes'),
                                                                      debug=False)
        print("init elec pipe")
        self.elec_pipe = fp.vat_invoice.pipeline.VatInvoicePipeline('elec', pars=dict(textline_method='textboxes'),
                                                                    debug=False)

        self._pipe = {'special': self.special_pipe,
                      'normal': self.normal_pipe,
                      'elec': self.elec_pipe}

    def get_pipe(self, type):
        return self._pipe[type]
