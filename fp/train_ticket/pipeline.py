# utf-8
import os
import importlib
import numpy as np
import cv2

from . import _blue_train_ticket_pipeline

importlib.reload(_blue_train_ticket_pipeline)
from ._blue_train_ticket_pipeline import BlueTrainTicketPipeline

from . import _excess_train_ticket_pipeline

importlib.reload(_excess_train_ticket_pipeline)
from ._excess_train_ticket_pipeline import ExcessTrainTicketPipeline


class TrainTicketPipeline(object):
    def __init__(self, invoice_type, debug=False):
        self.reset()
        if invoice_type == 'blue':
            self.pipe = BlueTrainTicketPipeline(debug=debug)
        elif invoice_type == 'red':
            raise NotImplemented
        elif invoice_type == 'excess':
            self.pipe = ExcessTrainTicketPipeline(debug=debug)
        else:
            raise NotImplemented

    def reset(self, is_blue=None, surface_image=None,
              textlines=None, template=None, guess=None,
              exit_msg=None):
        self.is_blue = is_blue
        self.surface_image = surface_image
        self.textlines = textlines
        self.template = template
        self.guess = guess
        self.exit_msg = exit_msg

    def __call__(self, image, no_background=False):
        res = self.pipe(image, no_background)
        self.reset(self.pipe.is_blue, self.pipe.surface_image,
                   self.pipe.textlines, self.pipe.template,
                   self.pipe.guess, self.pipe.exit_msg)
        return res
