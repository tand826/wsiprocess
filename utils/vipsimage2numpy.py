import pyvips
import numpy as np

# VipsImage to numpy array
img = pyvips.Image.new_from_file(
    "140087-5-2_0069_0020.jpg", access="sequential")
npimg = np.ndarray(
    buffer=img.write_to_memory(),
    dtype=np.uint8,
    shape=[img.height, img.width, img.bands])
