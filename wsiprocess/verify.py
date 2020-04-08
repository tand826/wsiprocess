from pathlib import Path
from .error import SizeError


class Verify:

    def __init__(
            self, save_to, filestem, method, start_sample,
            finished_sample, extract_patches):
        self.save_to = save_to
        self.filestem = filestem
        self.method = method
        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.extract_patches = extract_patches

    def verify_dirs(self):
        base_dir = Path(self.save_to)/self.filestem
        self.verify_dir(base_dir)
        if self.method == "none":
            self.verify_dir(base_dir/"patches"/"foreground")
        if self.method == "segmentation":
            self.verify_dir(base_dir/"masks")
        if self.start_sample:
            self.verify_dir(base_dir/"start_sample")
        if self.finished_sample:
            self.verify_dir(base_dir/"finished_sample")
        if self.extract_patches:
            self.verify_dir(base_dir/"patches")

    @staticmethod
    def verify_dir(path):
        if not Path(path).exists():
            Path(path).mkdir(parents=True)

    def verify_magnification(self, slide, magnification):
        basemsg = "Magnification for this slide has to be smaller than"
        msg = "{} {}".format(basemsg, slide.slide.magnification)
        assert slide.slide.magnification < magnification, msg

    @staticmethod
    def verify_sizes(
            wsi_width, wsi_height, patch_width, patch_height,
            overlap_width, overlap_height):
        if not (wsi_width > patch_width or wsi_height > patch_height):
            raise SizeError("WSI have to be larger than the patches.")
        if not (patch_width > overlap_width or patch_height > overlap_height):
            raise SizeError("Patches have to be larger than the overlap size.")
        if patch_width < 0 or patch_height < 0:
            raise SizeError("Patches has to be larger than 1.")
