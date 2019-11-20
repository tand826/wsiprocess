import pyvips
from pathlib import Path


class Slide:

    def __init__(self, path):
        self.slide = pyvips.Image.new_from_file(path)
        self.filename = Path(path).stem
        self.wsi_width = self.slide.width
        self.wsi_height = self.slide.height

    def get_thumbnail(self, size=500):
        thumb = self.slide.slide.thumbnail_image(size, height=size)
        thumb.pngsave("{}/{}/thumb.png".format())
