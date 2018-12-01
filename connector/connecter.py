from OCR import OCR as ocrVat
from OCR import OCRChinese as elecVat
import keras.backend.tensorflow_backend as K

global_model = ocrVat.load_model()
chinese_global_model = elecVat.load_model()

def OCR(image_path, typeP, attribute, thresholding = 160):
    """
        用来连接OCR调用，通过home/views.py来预加载全局模型
        imgae_path 输入图片路径，识别图片为行提取结果
    """
    global global_model
    global chinese_global_model
    with K.get_session().graph.as_default():
        if typeP == 'elec' :
            print('model:    chinese_global_model')
            out, _ = elecVat.predict(image_path, chinese_global_model, thresholding=thresholding)
        else:
            print('model:    global_model')
            out, _ = ocrVat.predict(image_path, global_model, thresholding=thresholding)

    return out

# caffe 模型
# import fp.TextBoxes.detect_textline as dt
# global_caffe_model = dt.load_caffe_model()
