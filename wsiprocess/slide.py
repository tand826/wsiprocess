# -*- coding: utf-8 -*-
"""Slide object to pass to annotation object and patcher object.
Slide is whole slide image, scanned with whole slide scanners.
Mannually you can make pyramidical tiff file, which you can handle just the
same as the scanned digital data, except for the magnification.
"""
from .error import SlideLoadError
from pathlib import Path
import numpy as np
from PIL import Image
import openslide


class Slide:
    """Slide object.

    Args:
        path (str): Path to the whole slide image file.
        backend (str): Openslide or pyivps.

    Attributes:
        path (str): Path to the whole slide image file.
        slide (pyvips.Image): pyvips Image object.
        wsi_width (int): Width of slide.
        wsi_height (int): Height of slide.
    """

    def __init__(self, path, backend="openslide"):
        self.path = path
        if not Path(path).exists():
            raise SlideLoadError("Slide File {} Not Found".format(path))
        self.filestem = Path(path).stem
        self.filename = Path(path).name
        self.backend = backend

        self.load_slide()

    def load_slide(self):
        if self.backend == "openslide":
            self.slide = openslide.OpenSlide(self.path)
            self.width, self.height = self.slide.dimensions
        elif self.backend == "pyvips":
            try:
                import pyvips
            except ImportError:
                raise ImportError("pyvips not installed")
            self.slide = pyvips.Image.new_from_file(self.path)

            self.width = self.slide.width
            self.height = self.slide.height
        else:
            raise NotImplementedError(
                "backend={} is not available".format(self.backend))
        self.set_properties()

    def __str__(self):
        return "wsiprocess.slide.Slide {} {}x{}".format(
            self.path, self.wsi_width, self.wsi_height)

    def export_thumbnail(self, save_as="./thumb.png", size=500):
        """Export thumbnail image.

        Args:
            save_as (str): Path to save as the thumbnail image.
            size (int, optional): Size of the exported thumbnail.
        """
        thumb = self.get_thumbnail(size)
        if self.backend == "openslide":
            thumb.save(save_as)
        elif self.backend == "pyvips":
            thumb.pngsave(save_as)

    def get_thumbnail(self, size=500):
        """Get thumbnail image.

        Args:
            size (int or tuple, optional): Size of the exported thumbnail.
        """
        if self.backend == "openslide":
            if isinstance(size, int):
                size = (size, size)
            return self.slide.get_thumbnail(size)
        elif self.backend == "pyvips":
            return self.slide.thumbnail_image(size)

    def set_properties(self):
        """Read the properties and set as attributes of slide obj.

        Attributes:
            magnification (int): Objective power of slide obj.
        """
        if self.backend == "openslide":
            properties = self.slide.properties
        elif self.backend == "pyvips":
            properties = {}
            for field in self.slide.get_fields():
                properties[field] = self.slide.get(field)
        for field in properties:
            setattr(self, field, properties.get(field))

        self.magnification = properties.get("openslide.objective-power")
        if self.magnification:
            self.magnification = int(self.magnification)

    def crop(self, x, y, w, h):
        if self.backend == "openslide":
            return self.slide.read_region((x, y), 0, (w, h))
        elif self.backend == "pyvips":
            patch = self.slide.crop(x, y, w, h)
            patch = np.ndarray(
                buffer=patch.write_to_memory(),
                dtype=np.uint8,
                shape=[patch.height, patch.width, patch.bands])
            return Image.fromarray(patch)
