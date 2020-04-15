# -*- coding: utf-8 -*-
"""Slide object to pass to annotation object and patcher object.
Slide is whole slide image, scanned with whole slide scanners.
Mannually you can make pyramidical tiff file, which you can handle just the
same as the scanned digital data, except for the magnification.
"""

import pyvips
from pathlib import Path
from .error import SlideLoadError


class Slide:
    """Slide object.

    Args:
        path (str): Path to the whole slide image file.

    Attributes:
        path (str): Path to the whole slide image file.
        slide (pyvips.Image): pyvips Image object.
        wsi_width (int): Width of slide.
        wsi_height (int): Height of slide.
    """

    def __init__(self, path):
        self.path = path
        if not Path(path).exists():
            raise SlideLoadError("Slide File {} Not Found".format(path))
        self.slide = pyvips.Image.new_from_file(path)

        self.filestem = Path(path).stem
        self.wsi_width = self.slide.width
        self.wsi_height = self.slide.height
        self.set_properties()

    def export_thumbnail(self, save_to=".", size=500):
        """Export thumbnail image.

        Args:
            save_to (str): Parent directory to save the thumbnail image.
            size (int, optional): Size of the exported thumbnail.
        """
        thumb = self.get_thumbnail(size)
        thumb.pngsave("{}/thumb.png".format(save_to))

    def get_thumbnail(self, size=500):
        """Get thumbnail image.

        Args:
            size (int, optional): Size of the exported thumbnail.
        """
        return pyvips.Image.thumbnail(self.path, size)

    def set_properties(self):
        """Read the properties and set as attributes of slide obj.

        Attributes:
            magnification (int): Objective power of slide obj.
        """
        for field in self.slide.get_fields():
            setattr(self, field, self.slide.get(field))
        if "openslide.objective-power" in self.slide.get_fields():
            self.magnification = self.slide.get("openslide.objective-power")
        else:
            self.magnification = None
