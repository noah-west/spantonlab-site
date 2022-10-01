import numpy as np

def get_contour(bytes):
    '''
    Translates bytes stored in the contour field of a flake to a ndarray representing an OpenCV contour
    '''

    contour = np.frombuffer(bytes, dtype = np.int32).reshape(-1, 2)
    return contour