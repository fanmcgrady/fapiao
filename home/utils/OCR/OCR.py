import time

import cv2
import keras.backend.tensorflow_backend as K
import numpy as np
import tensorflow as tf
from PIL import Image
from keras.layers import Input, Dense, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.layers.core import Permute
from keras.layers.normalization import BatchNormalization
from keras.layers.recurrent import GRU
from keras.layers.wrappers import Bidirectional
from keras.layers.wrappers import TimeDistributed
from keras.models import Model

from home import views

from keras import backend as K

char = ''
with open(r'home/utils/OCR/rcnn_dic.txt', encoding='utf-8') as f:
    for ch in f.readlines():
        ch = ch.strip('\r\n')
        char = char + ch
char = char + '卍'
n_classes = len(char)

char_to_id = {j: i for i, j in enumerate(char)}
id_to_char = {i: j for i, j in enumerate(char)}

# n_classes = 17
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)

class Timer(object):
    def __init__(self):
        self.total_time = 0.
        self.calls = 0
        self.start_time = 0.
        self.diff = 0.
        self.average_time = 0.

    def tic(self):
        self.start_time = time.time()

    def toc(self, average=True):
        self.diff = time.time() - self.start_time
        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff


def predict(img_path, base_model, thresholding=160):
    """
        thresholding 输入范围 0 - 255
        默认为160
        0 : 采用自动阈值
        > 0 : 采用人工设置的阈值
    """
    if thresholding > 255:
        thresholding = 255
    if thresholding < 0:
        thresholding = 0

    t = Timer()
    img = Image.open(img_path)
    im = img.convert('L')
    scale = im.size[1] * 1.0 / 64
    w = im.size[0] / scale
    w = int(w)
    # print('w:',w)

    im = im.resize((160, 32), Image.ANTIALIAS)
    img = np.array(im)
    h, w = img.shape

    if thresholding == 0:
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    else:
        for i in range(h):
            for j in range(w):
                if img[i, j] > thresholding:
                    img[i, j] = 255
                else:
                    img[i, j] = 0

    img = np.array(img)

    img = img.astype(np.float32) / 255.0 - 0.5
    X = img.reshape((32, 160, 1))
    X = np.array([X])

    t.tic()
    y_pred = base_model.predict(X)
    t.toc()
    # print("times,",t.diff)
    argmax = np.argmax(y_pred, axis=2)[0]
    y_pred = y_pred[:, :, :]
    out = K.get_value(K.ctc_decode(y_pred, input_length=np.ones(y_pred.shape[0]) * y_pred.shape[1], )[0][0])[:, :]
    out = u''.join([id_to_char[x] for x in out[0]])

    return out, im


def load_model():
    K.set_session(sess)
    modelPath = r'home/utils/OCR/model/weights-25.hdf5'
    print("加载OCR模型: {}".format(modelPath))
    input = Input(shape=(32, None, 1), name='the_input')
    m = Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same', name='conv1')(input)
    m = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='pool1')(m)
    m = Conv2D(128, kernel_size=(3, 3), activation='relu', padding='same', name='conv2')(m)
    m = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='pool2')(m)
    m = Conv2D(256, kernel_size=(3, 3), activation='relu', padding='same', name='conv3')(m)
    m = BatchNormalization(axis=3)(m)
    m = Conv2D(256, kernel_size=(3, 3), activation='relu', padding='same', name='conv4')(m)

    m = ZeroPadding2D(padding=(0, 1))(m)
    m = MaxPooling2D(pool_size=(2, 2), strides=(2, 1), padding='valid', name='pool3')(m)

    m = Conv2D(512, kernel_size=(3, 3), activation='relu', padding='same', name='conv5')(m)
    m = BatchNormalization(axis=3)(m)
    m = Conv2D(512, kernel_size=(3, 3), activation='relu', padding='same', name='conv6')(m)

    m = ZeroPadding2D(padding=(0, 1))(m)
    m = MaxPooling2D(pool_size=(2, 2), strides=(2, 1), padding='valid', name='pool4')(m)
    m = Conv2D(512, kernel_size=(2, 2), activation='relu', padding='valid', name='conv7')(m)
    m = BatchNormalization(axis=3)(m)

    m = Permute((2, 1, 3), name='permute')(m)
    m = TimeDistributed(Flatten(), name='timedistrib')(m)

    m = Bidirectional(GRU(256, return_sequences=True, implementation=2), name='blstm1')(m)
    m = Dense(256, name='blstm1_out', activation='linear', )(m)
    m = Bidirectional(GRU(256, return_sequences=True, implementation=2), name='blstm2')(m)
    y_pred = Dense(n_classes, name='blstm2_out', activation='softmax')(m)

    global_model = Model(inputs=input, outputs=y_pred)
    global_model.load_weights(modelPath)

    # 预先预测一次
    print("Test model")
    global_model.predict(np.zeros((1, 32, 160, 1)))
    print("Test model over")

    return global_model


global_model = None
def OCR(image_path, base_model=None):
    """
        imgae_path 输入图片路径，识别图片为行提取结果
        color: 0 二值， 1 灰度， 2 彩色
        base_model 为加载模型，这个模型最好在服务器启动时加载，计算时作为参数输入即可，减少加载模型所需要的时间
    """
    global global_model
    if base_model is None:
        # base_model = views.global_model
        if global_model is None:
            base_model = load_model()
            global_model = base_model
        else:
            base_model = global_model
    out, _ = predict(image_path, base_model)

    return out
