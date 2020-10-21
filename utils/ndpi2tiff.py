# convert ndpi to tiff
import openslide
import numpy as np
import pyvips


slide = openslide.OpenSlide("test2.ndpi")
# print(slide.dimensions)
patch = np.array(slide.read_region((0, 0), 0, (20480, 21248)))[:, :, :3]
# print(patch.shape)
vimg = pyvips.Image.new_from_memory(patch.tobytes(), 20480, 21248, 3, 'uchar')
# print(vimg.width, vimg.height)
vimg.tiffsave("out_op.tiff", compression="jpeg", pyramid=True, tile=True)
