from django.conf import settings
import numpy as np
import os
import re

LUTEXTRACT = re.compile('([0-9.]+\s+){256}[0-9.]+')

def get_contour(bytes):
    '''
    Translates bytes stored in the contour field of a flake to a ndarray representing an OpenCV contour
    '''

    contour = np.frombuffer(bytes, dtype = np.int32).reshape(-1, 2)
    return contour

def extract_LUT(curves_path):
    '''
    Exports GIMP paths file into a look-up table for OpenCV
    
    ----------------
    Params:

    curves_path : path-like object
        Path to the curves files from which to extract the LUT

    Returns:

    LUT_list : list
        List of numpy arrays containing the look-up tables for channels value, red, green, blue, alpha in order 

    '''

    LUT_list = []
    with open(curves_path) as f:
        for line in f:
            result = LUTEXTRACT.search(line)
            if result:
                try:
                    arr = np.fromstring(result.group(), sep = " ")
                except ValueError:
                    print("Invalid LUT table for {}".format(curves_path))
                    return
                LUT_list.append(np.float32(arr[1:])) # We skip the first number because its simply the number of values
    
    return LUT_list

# Lookup tables for processing flake images. Loaded into memory at runtime from static files.
lookup_tables = []

LUT_path = os.path.join(settings.STATIC_ROOT, 'flake_app\\LUT')

for filename in os.listdir(LUT_path):
    LUT_file = os.path.join(LUT_path, filename)

    LUT_list = extract_LUT(LUT_file)
    if LUT_list:
        lookup_tables.append(LUT_list)
        