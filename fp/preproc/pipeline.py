'''
Preprocess Pipeline
'''

import importlib

from ..util import check

importlib.reload(check)


class PreprocPipeline(object):
    def __init__(self):
        self.colored = None
        self.binarized = None

    def __call__(self, image):
        assert check.valid_image(image, colored=1)
        self.colored = check.is_colored(image)
        self.binarized = check.is_binarized(image)
        return True
