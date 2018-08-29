import os

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))

USE_CUDA = False

TEXTLINE_CLASSIFY_LENET_WEIGHT = os.path.join(PACKAGE_DIR, 'data\lenet_weights.pkl')

EPSILON = 0.0001