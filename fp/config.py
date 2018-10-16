# import os
#
# PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
#
# USE_CUDA = False
#
# TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, 'data\lenet_weights.pkl')
#
# EPSILON = 0.0001
#
# ####################
# # Textline detection
# ####################
# TEXTLINE_DETECT_USE_CUDA = False # for textline detection
# TEXTLINE_TRAIN_TICKET_CAFFE = \
# dict(prototxt=os.path.join(PACKAGE_DIR, 'TextBoxes\models\\fapiao.prototxt'),
#      caffemodel=os.path.join(PACKAGE_DIR, 'TextBoxes\models\\fapiao.caffemodel'))
# TEXTLINE_VAT_INVOICE_CAFFE = \
# dict(prototxt=os.path.join(PACKAGE_DIR, 'TextBoxes\models\\fapiao.prototxt'),
#      caffemodel=os.path.join(PACKAGE_DIR, 'TextBoxes\models\\fapiao.caffemodel'))
#
# ##########################
# # Textline classification
# ##########################
# TEXTLINE_CLASSIFY_CUDA = False
# TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, 'data\lenet_weights.pkl')
#
# #################
# # Template Match
# #################
#
# TEMPLATE_TRAIN_TICKET_BLUE = os.path.join(PACKAGE_DIR,
#                                           'data\\template_traintk_blue.yaml')
# TEMPLATE_TRAIN_TICKET_EXCESS = os.path.join(PACKAGE_DIR,
#                                             'data\\template_train_ticket_excess.yaml')
# WIREFRAME_TEMPLATE_VAT = os.path.join(PACKAGE_DIR,
#                                       'data\\vat_invoice_special_wire.yaml')

import os

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))

USE_CUDA = False

TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, 'data/lenet_weights.pkl')

EPSILON = 0.0001

####################
# Textline detection
####################
TEXTLINE_DETECT_USE_CUDA = False  # for textline detection
TEXTLINE_TRAIN_TICKET_CAFFE = \
    dict(prototxt=os.path.join(PACKAGE_DIR, 'TextBoxes/models/fapiao.prototxt'),
         caffemodel=os.path.join(PACKAGE_DIR, 'TextBoxes/models/fapiao.caffemodel'))
TEXTLINE_VAT_INVOICE_CAFFE = \
    dict(prototxt=os.path.join(PACKAGE_DIR, 'TextBoxes/models/fapiao.prototxt'),
         caffemodel=os.path.join(PACKAGE_DIR, 'TextBoxes/models/fapiao.caffemodel'))

##########################
# Textline classification
##########################
TEXTLINE_CLASSIFY_CUDA = False
TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, 'data/lenet_weights.pkl')

#################
# Template Match
#################

TEMPLATE_TRAIN_TICKET_BLUE = os.path.join(PACKAGE_DIR,
                                          'data/template_traintk_blue.yaml')
TEMPLATE_TRAIN_TICKET_EXCESS = os.path.join(PACKAGE_DIR,
                                            'data/template_train_ticket_excess.yaml')
WIREFRAME_TEMPLATE_VAT = os.path.join(PACKAGE_DIR,
                                      'data/vat_invoice_special_wire.yaml')