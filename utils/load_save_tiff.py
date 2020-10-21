import pyvips

# load image
image = pyvips.Image.new_from_file("CMU-1.tiff")

# save
image.tiffsave("out.tiff", compression="jpeg", pyramid=True, tile=True)
