import numpy as np
import os

os.environ['GLOG_minloglevel'] = '3'

import glob
import pandas
import sys
import datetime

from .nms import nms
from .util import timewatch

from .. import config

## load caffe package
# pwd = os.getcwd()
caffe_root = os.path.dirname(os.path.realpath(__file__))  # Make sure this file is on the caffe root path
# os.chdir(caffe_root)
sys.path.insert(0, os.path.join(caffe_root, 'python'))
import caffe

if config.TEXTLINE_DETECT_USE_CUDA is True:
    caffe.set_device(0)
    caffe.set_mode_gpu()
else:
    caffe.set_mode_cpu()


class _Detect(object):
    def __init__(self):
        pass

    def __call__(self, image):
        raise NotImplemented


class TextBoxesDetect(_Detect):
    def __init__(self, \
                 model_def='models/fapiao.prototxt', \
                 model_weights='models/fapiao.caffemodel', \
                 scales=((700, 700),),  # (700,1600),(1600,1600)),  \
                 confidence_thres=0.6):  #
        self.model_def = model_def
        self.model_weights = model_weights
        print(self.model_def, self.model_weights)
        self.net = caffe.Net(model_def,  # defines the structure of the model
                             model_weights,  # contains the trained weights
                             caffe.TEST)  # use test mode (e.g., don't perform dropout)
        self.scales = scales
        self.confidence_thres = confidence_thres

    def __call__(self, image):
        predictions = self.detect(image)
        return predictions

    def detect_to_cvs(self, image, cvs_file=None):
        predictions = self.detect(image)
        if cvs_file is not None:
            df = pandas.DataFrame(predictions, columns=["x", "y", "width", "height", "confidence"])
            df.to_csv(cvs_file, index=False)

    def set_net_model(self, model_def, model_weights):
        self.model_def = model_def
        self.model_weights = model_weights
        self.net = caffe.Net(model_def, model_weights, caffe.TEST)

    def detect(self, image):
        # image=caffe.io.load_image(image_file)
        image_height, image_width, channels = image.shape
        print(image.shape)
        _rlts = []
        for scale in self.scales:
            image_resize_height = scale[0]
            image_resize_width = scale[1]
            transformer = caffe.io.Transformer({'data': (1, 3, image_resize_height, image_resize_width)})
            transformer.set_transpose('data', (2, 0, 1))
            transformer.set_mean('data', np.array([104, 117, 123]))  # mean pixel
            transformer.set_raw_scale('data',
                                      255)  # the reference model operates on images in [0,255] range instead of [0,1]
            transformer.set_channel_swap('data',
                                         (2, 1, 0))  # the reference model has channels in BGR order instead of RGB

            self.net.blobs['data'].reshape(1, 3, image_resize_height, image_resize_width)
            transformed_image = transformer.preprocess('data', image)
            self.net.blobs['data'].data[...] = transformed_image
            # Forward pass.
            detections = self.net.forward()['detection_out']

            # Parse the outputs.
            det_label = detections[0, 0, :, 1]
            det_conf = detections[0, 0, :, 2]
            det_xmin = detections[0, 0, :, 3]
            det_ymin = detections[0, 0, :, 4]
            det_xmax = detections[0, 0, :, 5]
            det_ymax = detections[0, 0, :, 6]
            top_indices = [i for i, conf in enumerate(det_conf) if conf >= self.confidence_thres]
            top_conf = det_conf[top_indices]
            top_xmin = det_xmin[top_indices]
            top_ymin = det_ymin[top_indices]
            top_xmax = det_xmax[top_indices]
            top_ymax = det_ymax[top_indices]

            for i in range(top_conf.shape[0]):
                xmin = int(round(top_xmin[i] * image.shape[1]))
                ymin = int(round(top_ymin[i] * image.shape[0]))
                xmax = int(round(top_xmax[i] * image.shape[1]))
                ymax = int(round(top_ymax[i] * image.shape[0]))
                xmin = max(1, xmin)
                ymin = max(1, ymin)
                xmax = min(image.shape[1] - 1, xmax)
                ymax = min(image.shape[0] - 1, ymax)
                score = top_conf[i]
                dt_result = [xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax, score]
                _rlts.append(dt_result)

        _rlts = sorted(_rlts, key=lambda x: -float(x[8]))
        nms_flag = nms(_rlts, 0.03)
        det_results = []
        for k, dt in enumerate(_rlts):
            if nms_flag[k]:
                xmin = dt[0]
                ymin = dt[1]
                xmax = dt[2]
                ymax = dt[5]
                conf = dt[8]
                det_results.append([xmin, ymin, xmax - xmin + 1, ymax - ymin + 1, conf])
        return det_results  # [[(x,y,width,height),confidence],......]


if __name__ == "__main__":
    print('args: image_dir_path[option]')
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
    else:
        image_path = '/home/gaolin/data/fapiao'
    im_names = glob.glob(os.path.join(image_path, "*.jpg"))

    detector = TextBoxesDetect()
    for im_name in im_names:
        cvs_file = im_name.replace('.jpg', '.csv')
        tim = timewatch.start_new()
        im = caffe.io.load_image(im_name)
        # im =cv2.imread(im_name,1)
        detector(im)
        # detector.detect_to_cvs(im, cvs_file)
        print(im_name)
        print("Done in : ", tim.get_elapsed_seconds(), " seconds")
