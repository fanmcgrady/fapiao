from OCR import OCR2 as ocrVat
from OCR import OCR3 as veryVat
import keras.backend.tensorflow_backend as K
import time

verify_global_model = veryVat.load_model()
global_model = ocrVat.load_model()


# global_model._make_predict_function()
# verify_global_model = veryVat.load_model()
# verify_global_model._make_predict_function()

def OCR(image_path, typeP, attribute, thresholding = 160):
    """
        用来连接OCR调用，通过home/views.py来预加载全局模型
        imgae_path 输入图片路径，识别图片为行提取结果
    """

    time11 = time.time()

    global verify_global_model
    global global_model

    with K.get_session().graph.as_default():
        if typeP == 'normal' and attribute == 'verifyCode':
            print('model:    3_global_model')
            out, _ = veryVat.predict(image_path, verify_global_model)
        else:
            print('model:    global_model')
            out, _ = ocrVat.predict(image_path, global_model)

    time12 = time.time()
    print(attribute + ' 识别耗时：   ' + str(time12 - time11))

    return out

# caffe 模型
# import fp.TextBoxes.detect_textline as dt
# global_caffe_model = dt.load_caffe_model()
