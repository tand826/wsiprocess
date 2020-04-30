# -*- coding: utf-8 -*-
"""Annotation object.

Annotation object is optional metadata for slide.
This object can handle ASAP or WSIViewer style annotation.
By adding annotationparser, you can process annotation data from other types of
annotation tools.


Example:
    Loading annotation data:: python

        import wsiprocess as wp
        annotation = wp.annotation("path_to_annotation_file.xml")
"""

import cv2
import numpy as np
from pathlib import Path
from .annotationparser.parser_utils import detect_type


class Annotation:

    def __init__(self, path):
        self.path = path
        self.read_annotation()
        self.masks = {}
        self.contours = {}

    def __str__(self):
        return "wsiprocess.annotation.Annotation {}".format(self.path)

    def read_annotation(self, annotation_type=False):
        """Parse the annotation data.

        WSIViewer is going to be added as a annotation type.
        Currently, ASAP is available.

        Args:
            annotation_type (str): If provided, pass the auto type detection.
        """
        if not annotation_type:
            annotation_type = detect_type(self.path)
        if annotation_type == "ASAP":
            from .annotationparser.ASAP_parser import AnnotationParser
        elif annotation_type == "pathology_viewer":
            from .annotationparser.pathology_viewer_parser import AnnotationParser
        elif annotation_type == "Empty":
            class AnnotationParser:
                classes = []
                mask_coords = {}

                def __init__(self, path):
                    print("Annotation File is Empty")
        try:
            parsed = AnnotationParser(self.path)
        except Exception as e:
            raise NotImplementedError(
                "[{e}] Could not parse {}".format(e, self.path))
        self.classes = parsed.classes
        self.mask_coords = parsed.mask_coords

    def make_masks(self, slide, rule=False, foreground=False, size=2000):
        """Make masks from the slide and rule.

        Masks are for each class and foreground area.

        Args:
            slide (wsiprocess.slide.Slide): Slide object
            rule (:obj:`wsiprocess.rule.Rule`, optional): Rule object
            foreground (bool, optional): Whether to crop only from the
                foreground area.
            size (int, optional): Size of foreground mask on calculating with
                the Otsu Thresholding.
        """
        self.base_masks(slide.wsi_height, slide.wsi_width)
        self.main_masks()
        if rule:
            self.classes = list(set(self.classes) & set(rule.classes))
            self.include_masks(rule)
            self.exclude_masks(rule)
        if foreground:
            self.make_foreground_mask(slide, size)

    def base_masks(self, wsi_height, wsi_width):
        """Make base masks.

        Args:
            wsi_height (int): The height of base masks.
            wsi_width (int): The width of base masks.
        """
        for cls in self.classes:
            self.base_mask(cls, wsi_height, wsi_width)

    def base_mask(self, cls, wsi_height, wsi_width):
        """ Masks have same size of as the slide.

        Masks are canvases of 0s.

        Args:
            cls (str): Class name for each mask.
            wsi_height (int): The height of base masks.
            wsi_width (int): The width of base masks.
        """
        self.masks[cls] = np.zeros((wsi_height, wsi_width), dtype=np.uint8)

    def main_masks(self):
        """Main masks

        Write border lines following the rule and fill inside with 255.
        """
        for cls in self.classes:
            contours = np.array(self.mask_coords[cls])
            for contour in contours:
                self.masks[cls] = cv2.drawContours(
                    self.masks[cls], [np.int32(contour)], 0, True, thickness=cv2.FILLED)

    def include_masks(self, rule):
        """Merge masks following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        self.masks_include = self.masks.copy()
        for cls in self.classes:
            if hasattr(rule, cls):
                for include in getattr(rule, cls)["includes"]:
                    if include in self.masks:
                        self.masks_include[cls] = cv2.bitwise_or(
                            self.masks[cls], self.masks[include])
        self.masks = self.masks_include

    def exclude_masks(self, rule):
        """Exclude area from base mask with following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        self.masks_exclude = self.masks.copy()
        for cls in self.classes:
            if hasattr(rule, cls):
                for exclude in getattr(rule, cls)["excludes"]:
                    if exclude in self.masks:
                        overlap_area = cv2.bitwise_and(
                            self.masks[cls], self.masks[exclude])
                        self.masks_exclude[cls] = cv2.bitwise_xor(
                            self.masks[cls], overlap_area)
        self.masks = self.masks_exclude

    def make_foreground_mask(self, slide, size=2000):
        """Make foreground mask.

        With otsu thresholding, make simple foreground mask.

        Args:
            slide (wsiprocess.slide.Slide): Slide object.
            size (int, optional): Size of foreground mask on calculating with
                the Otsu Thresholding.
        """
        if "foreground" in self.classes:
            return
        thumb = slide.get_thumbnail(size)
        thumb = np.ndarray(
            buffer=thumb.write_to_memory(),
            dtype=np.uint8,
            shape=[thumb.height, thumb.width, thumb.bands])
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        _, th = cv2.threshold(
            thumb_gray, 0, 1, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        self.masks["foreground"] = cv2.resize(th, (slide.width, slide.height))
        self.classes.append("foreground")

    def export_thumb_masks(self, save_to=".", size=512):
        """Export thumbnail of masks.

        For prior check, export thumbnails of masks.

        Args:
            save_to (str): Parent directory to save the thumbnails.
            size (int): Length of the long side of thumbnail.
        """
        for cls in self.masks.keys():
            self.export_thumb_mask(cls, save_to, size)

    def export_thumb_mask(self, cls, save_to=".", size=512):
        """Export a thumbnail of one of the masks.

        For prior check, export one thumbnail of one of the masks.

        Args:
            cls (str): Class name for each mask.
            save_to (str, optional): Parent directory to save the thumbnails.
            size (int, optional): Length of the long side of thumbnail.
        """
        mask = self.masks[cls]
        height, width = mask.shape
        scale = max(size / height, size / width)
        mask_resized = cv2.resize(mask, dsize=None, fx=scale, fy=scale)
        mask_scaled = mask_resized * 255
        cv2.imwrite(str(Path(save_to)/"{}_thumb.png".format(cls)), mask_scaled)

    def export_masks(self, save_to):
        """Export binary mask images.

        For later computing such as segmentation, export the mask images.
        Exported masks have 0 or 1 binary data.

        Args:
            save_to (str): Parent directory to save the thumbnails.
        """
        for cls in self.masks.keys():
            self.export_mask(save_to, cls)

    def export_mask(self, save_to, cls):
        """Export one binary mask image.

        Export mask image with 0 or 1 binaries.

        Args:
            save_to (str): Parent directory to save the thumbnails.
            cls (str): Class name for each mask.
        """
        cv2.imwrite(str(Path(save_to)/"{}.png".format(cls)),
                    self.masks[cls], (cv2.IMWRITE_PXM_BINARY, 1))
