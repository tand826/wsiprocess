# -*- coding: utf-8 -*-
"""Verification script runs before the patcher works.
Verify class works for verification of the output directory, annotation files,
rule files, etc. Mainly runs for cli.
"""

from pathlib import Path
from .error import SizeError


class Verify:
    """Verification class.

    Args:
        save_to (str): The root of the output directory.
        filestem (str): The name of the output directory.
        method (str): Method name to run. One of {"none", "classification",
            "detection", "segmentation}
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): Whether to save patches when Patcher runs.

    Attributes:
        save_to (str): The root of the output directory.
        filestem (str): The name of the output directory.
        method (str): Method name to run. One of {"none", "classification",
            "detection", "segmentation}
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): Whether to save patches when Patcher runs.
    """

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
        """Ensure the output directories exists for each tasks.
        """
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
        """Make output directory.
        """
        if not Path(path).exists():
            Path(path).mkdir(parents=True)

    def verify_magnification(self, slide, magnification):
        """Check if the slide has data for the magnification the user specified.

        Args:
            slide (wp.slide.Slide): Slide object to check.
            magnification (int): Target magnification value which has to be
                smaller than the magnification of the slide.
        """
        basemsg = "Magnification for this slide has to be smaller than"
        msg = "{} {}".format(basemsg, slide.slide.magnification)
        assert slide.slide.magnification < magnification, msg

    @staticmethod
    def verify_sizes(
            wsi_width, wsi_height, patch_width, patch_height,
            overlap_width, overlap_height):
        """Verify the sizes of the slide, the patch and the overlap area.

        Args:
            wsi_width (int): The width of the slide.
            wsi_height (int): The height of the slide.
            patch_width (int): The width of the output patches.
            patch_height (int): The height of the output patches.
            overlap_width (int): The width of the overlap areas of patches.
            overlap_height (int): The height of the overlap areas of patches.

        Raises:
            wsiprocess.error.SizeError: If the sizes are invalid.
        """
        if not (wsi_width > patch_width or wsi_height > patch_height):
            raise SizeError("WSI have to be larger than the patches.")
        if not (patch_width > overlap_width or patch_height > overlap_height):
            raise SizeError("Patches have to be larger than the overlap size.")
        if patch_width < 0 or patch_height < 0:
            raise SizeError("Patches has to be larger than 1.")
