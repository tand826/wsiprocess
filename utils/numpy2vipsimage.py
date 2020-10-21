import matplotlib.pyplot as plt
import pyvips

img = plt.imread("lena_std.tif")
vimg = pyvips.Image.new_from_memory(img, 512, 512, 3, 'uchar')
vimg.tiffsave(
    "out_vimg_pyramid.tiff", compression="jpeg", pyramid=True, tile=True)
