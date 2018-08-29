'''Base class for Functor'''

class _Functor(object):
    def __init__(self):
        pass
    
    def __call__(self, image):
        raise NotImplemented