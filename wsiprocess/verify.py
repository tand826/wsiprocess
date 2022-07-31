# -*- coding: utf-8 -*-
"""Verification script runs before the patcher works.
Verify class works for verification of the output directory, annotation files,
rule files, etc. Mainly runs for cli.
"""

import warnings
from pathlib import Path
from .error import SizeError, OnParamError


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
        extract_patches (bool): [Deleted]Whether to save patches when Patcher
            runs.
        no_patches (bool): Whether to save patches when Patcher runs.

    Attributes:
        save_to (str): The root of the output directory.
        filestem (str): The name of the output directory.
        method (str): Method name to run. One of {"none", "classification",
            "detection", "segmentation}
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): [Deleted]Whether to save patches when Patcher
            runs.
        no_patches (bool): Whether to save patches when Patcher runs.
    """

    def __init__(
            self, save_to, filestem, method, start_sample,
            finished_sample, no_patches, crop_bbox):
        self.save_to = save_to
        self.filestem = filestem
        self.method = method
        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.no_patches = no_patches
        self.crop_bbox = crop_bbox

    def make_dirs(self):
        """Ensure the output directories exists for each tasks.
        """
        base_dir = Path(self.save_to)/self.filestem
        if base_dir.exists():
            warnings.warn(
                "saving results to {}, but it already exists.".format(base_dir)
            )
        self.make_dir(base_dir)
        if self.method == "evaluation" and not self.no_patches:
            self.make_dir(base_dir/"patches"/"foreground")
        if self.method == "segmentation":
            self.make_dir(base_dir/"masks")
        if self.start_sample:
            self.make_dir(base_dir/"start_sample")
        if self.finished_sample:
            self.make_dir(base_dir/"finished_sample")
        if self.crop_bbox:
            self.make_dir(base_dir/"mini_patches")

    @staticmethod
    def make_dir(path):
        """Make output directory.
        """
        if not Path(path).exists():
            Path(path).mkdir(parents=True)

    def magnification(self, slide, magnification):
        """Check if the slide has data for the magnification the user specified.

        Args:
            slide (wp.slide.Slide): Slide object to check.
            magnification (int): Target magnification value which has to be
                smaller than the magnification of the slide.
        """
        basemsg = "Magnification for this slide has to be smaller than"
        msg = "{} {}".format(basemsg, slide.slide.magnification)
        assert slide.slide.magnification < magnification, msg

    def sizes(
            self, wsi_width, wsi_height, offset_x, offset_y,
            patch_width, patch_height, overlap_width, overlap_height,
            dot_bbox_width=False, dot_bbox_height=False):
        """Verify the sizes of the slide, the patch and the overlap area.

        Raises:
            wsiprocess.error.SizeError: If the sizes are invalid.
        """
        if wsi_width < patch_width or wsi_height < patch_height:
            raise SizeError("WSI have to be larger than the patches.")
        if wsi_width < offset_x or wsi_height < offset_y:
            raise SizeError("Offset must be less than wsi size.")
        if patch_width <= overlap_width or patch_height <= overlap_height:
            raise SizeError("Patches have to be larger than the overlap size.")
        if patch_width < 0 or patch_height < 0:
            raise SizeError("Patches has to be larger than 1.")
        if dot_bbox_width is not False and dot_bbox_width > patch_width:
            raise SizeError("Translated bbox is larger than patch width.")
        if dot_bbox_height is not False and dot_bbox_height > patch_height:
            raise SizeError("Translated bbox is larger than patch height.")

    def on_params(self, on_annotation, on_foreground):
        """Verify the ratio of on_annotation.

        Args:
            on_annotation (float): Overlap ratio of patches and annotations.
            on_foreground (float): Overlap ratio of patches and foreground area

        Raises:
            wsiprocess.error.SizeError: If the sizes are invalid.
        """
        if not isinstance(on_annotation, bool):
            if on_annotation <= 0 or on_annotation > 1:
                raise OnParamError(
                    "on_annotation is between 0 and 1 excluding 0.")

        if on_foreground <= 0 or on_foreground > 1:
            raise OnParamError(
                "on_foreground is between 0 and 1 excluding 0.")
