import os

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))

USE_CUDA = False
EPSILON = 0.0001

TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, '../data/lenet_weights.pkl')

TEMPLATE_TRAIN_TICKET_BLUE = os.path.join(PACKAGE_DIR,
                                          '../data/template_traintk_blue.yaml')
TEMPLATE_TRAIN_TICKET_EXCESS = os.path.join(PACKAGE_DIR,
                                            '../data/template_train_ticket_excess.yaml')
