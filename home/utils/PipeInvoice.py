import os
import sys
import importlib
import numpy as np
import cv2
import matplotlib.pyplot as pl

import fp

importlib.reload(fp)


def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def getPipe(dset_root, file_name, type, idStandard=False):
    filepath = os.path.join(dset_root, file_name)
    out_filename = file_name.replace('upload', 'out')
    out_filename = os.path.join(dset_root, out_filename)

    if type == 'excess':
        pipe = fp.train_ticket.TrainTicketPipeline(invoice_type='excess', debug=False)
        im = cv2.imread(filepath, 1)
        ok = pipe(im, idStandard)
        print('ok' if ok else 'fail')

        cv2.imwrite(out_filename, pipe.surface_image)

        return out_filename, 3, pipe.textlines
    elif type == 'blue':
        pipe = fp.train_ticket.BlueTrainTicketPipeline(debug=False)
        im = cv2.imread(filepath, 1)
        ok = pipe(im, no_background=idStandard)
        print('ok' if ok else 'fail')

        out_filename = file_name.replace('upload', 'out')
        out_filename = os.path.join(dset_root, out_filename)

        cv2.imwrite(out_filename, pipe.surface_image)

        return out_filename, 1, pipe.textlines
        '''elif type == 'red':
        pipe = fp.train_ticket.TrainTicketPipeline('red', debug=False)
        im = cv2.imread(filepath, 1)
        ok = pipe(im, no_background=idStandard)
        print('ok:' + ok)
        return pipe.surface_image, 2, None'''
    else:
        print('type is red or else')
        return None
