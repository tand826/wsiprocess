import pyvips
from pathlib import Path


class Slide:

    def __init__(self, path):
        self.slide = pyvips.Image.new_from_file(path)
        self.magnification = self.slide.get("openslide.objective-power")
        self.filename = Path(path).stem
        self.wsi_width = self.slide.width
        self.wsi_height = self.slide.height
        self.set_properties()

    def export_thumbnail(self, save_to, size=500):
        thumb = self.get_thumbnail(size)
        thumb.pngsave("{}/thumb.png".format(save_to))

    def get_thumbnail(self, size=500):
        return self.slide.slide.thumbnail_image(size, height=size)

    def set_properties(self):
        for field in self.slide.get_fields():
            setattr(self, field, self.slide.get(field))
