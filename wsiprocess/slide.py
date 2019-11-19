import openslide
from openslide.deepzoom import DeepZoomGenerator


class Slide:

    def __init__(self, path):
        self.slide = openslide.OpenSlide(path)
        self.wsi_width, self.wsi_height = self.slide.dimensions

    def to_patch(self, method, patch_width, overlap_width, annotation=False,
                 only_foreground=False, patch_on_annotated=False,
                 start_sample=False, finished_sample=False,
                 extract_patches=False, magnification=40):
        dz = DeepZoomGenerator(self.slide, tile_size=patch_width, overlap=overlap_width)
        if method == "none":
            self.save_patch_none()

    def save_patch(self):
        pass

    def is_foreground(self):
        pass

    def on_annotation(self):
        pass

    def save_patch_none_annotation(self):
        pass

    def save_patch_none_noannotation(self):
        pass

    def save_patch_classification_annotation(self):
        pass

