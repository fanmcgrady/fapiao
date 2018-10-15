import os
import sys
import glob

import detect_textline as dt
from util import timewatch

import importlib

importlib.reload(dt)

import caffe

proc_train_ticket = False  ##process tickets?

if __name__ == "__main__":
    im_names = []
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            im_names.append(sys.argv[i])
    else:
        if proc_train_ticket:
            image_path = '/home/gaolin/data/train_ticket'
        else:
            image_path = '/home/gaolin/data/fapiao'
        im_names = glob.glob(os.path.join(image_path, "*.jpg"))

    '''
    textline detector class
    args:[option]
    model_def = prototxt filepath
    model_weights = caffemodel filepath
    scales= ((300,300),(700,700),(1600,1600)...)
    confidence_thres = 0.6
    '''
    if proc_train_ticket:
        detector = dt.TextBoxesDetect(model_def='/home/gaolin/TextBoxes/models/train_ticket.prototxt',
                                      model_weights='/home/gaolin/TextBoxes/models/train_ticket.caffemodel',
                                      scales=((300, 300), (700, 700), (300, 700)))
    else:
        detector = dt.TextBoxesDetect(model_def='/home/tangpeng/fapiao/fp/fp/TextBoxes/models/fapiao.prototxt',
                                      model_weights='/home/tangpeng/fapiao/fp/fp/TextBoxes/models/fapiao.caffemodel',
                                      scales=((700, 700), (700, 1600), (1600, 1600)))

    for im_name in im_names:
        cvs_file = im_name.replace('.jpg', '_tb.csv')
        tim = timewatch.start_new()
        print("Start process: ", im_name)
        im = caffe.io.load_image(im_name)
        # detector(im)
        # output to the specified cvs file 
        detector.detect_to_cvs(im, cvs_file)

        print("Done in : ", tim.get_elapsed_seconds(), " seconds")
