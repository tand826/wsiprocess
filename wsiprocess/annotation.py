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

    Loading annotation data from image:: python

        import wsiprocess as wp
        annotation = wp.annotation("")
"""

import cv2
import numpy as np
from pathlib import Path
from .annotationparser.parser_utils import detect_type


class Annotation:

    def __init__(self, path, is_image=False, slidename=False):
        """Initialize the anntation object.

        Args:
            path(str): Path to the anntation data.
                Text data made with "WSIDissector" or "ASAP", and Image data
                (non-pyramidical) are available.
            is_image(bool): Whether the image is image.
        """
        self.path = path
        self.slidename = slidename
        self.dot_bbox_width = self.dot_bbox_height = 0
        self.is_image = is_image
        self.classes = []
        if not self.is_image:
            self.read_annotation()
        self.masks = {}
        self.contours = {}

    def __str__(self):
        return "wsiprocess.annotation.Annotation {}".format(self.path)

    def read_annotation(self, annotation_type=False):
        """Parse the annotation data.

        Args:
            annotation_type (str): If provided, pass the auto type detection.
        """
        if not annotation_type:
            annotation_type = detect_type(self.path)
        if annotation_type == "ASAP":
            from .annotationparser.ASAP_parser import AnnotationParser
            parsed = AnnotationParser(self.path)
        elif annotation_type == "WSIDissector":
            from .annotationparser.wsidissector_parser import AnnotationParser
            parsed = AnnotationParser(self.path)
        elif annotation_type == "SlideRunner":
            from .annotationparser.SlideRunner_parser import AnnotationParser
            parsed = AnnotationParser(self.path, self.slidename)
        elif annotation_type == "QuPath":
            from .annotationparser.QuPath_parser import AnnotationParser
            parsed = AnnotationParser(self.path)
        elif annotation_type == "Empty":
            class AnnotationParser:
                classes = []
                mask_coords = {}

                def __init__(self, path):
                    print("Annotation File is Empty")
            parsed = AnnotationParser(self.path)
        self.classes = parsed.classes
        self.mask_coords = parsed.mask_coords

    def dot_to_bbox(self, width=30, height=False):
        """Translate dot annotations to bounding boxes.

        If the len(self.mask_coords[cls][idx]) is 1, the annotation is a dot.
        And, the dot is the midpoint of the bounding box.

        Args:
            width (int): Width of the translated bounding box.
            height (int): Height of the translated bounding box. If not set,
                height is equal to width.
        """
        self.dot_bbox_width = width
        self.dot_bbox_height = width if not height else height

        for cls, coords in self.mask_coords.items():
            for idx, coord in enumerate(coords):
                if len(coord) == 1:
                    center_x = coord[0][0]
                    center_y = coord[0][1]
                    left = int(center_x - self.dot_bbox_width / 2)
                    top = int(center_y - self.dot_bbox_height / 2)
                    right = int(center_x + self.dot_bbox_width / 2)
                    bottom = int(center_y + self.dot_bbox_height / 2)
                    lefttop = [left, top]
                    righttop = [right, top]
                    leftbottom = [left, bottom]
                    rightbottom = [right, bottom]
                    self.mask_coords[cls][idx] = [
                        lefttop, righttop, rightbottom, leftbottom]

    def add_class(self, classes):
        for cls in classes:
            self.classes.append(cls)

    def from_image(self, mask, cls):
        """Load mask data from an image.

        Args:
            mask(numpy.ndarray): 2D mask image with background as 0, and
                foreground as 255.
            cls(str): Name of the class of the mask image.
        """
        assert len(mask.shape) == 2, "Mask image is not 2D."
        assert self.classes, "Classes are not set yet."
        self.masks[cls] = mask

    def make_masks(
            self, slide, rule=False, foreground="otsu", size=2000,
            min_=30, max_=190):
        """Make masks from the slide and rule.

        Masks are for each class and foreground area.

        Args:
            slide (wsiprocess.slide.Slide): Slide object
            rule (:obj:`wsiprocess.rule.Rule`, optional): Rule object
            foreground (str, optional): This can be {otsu, minmax}. If not set,
                Annotation don't make foreground mask.
            size (int, optional): Size of foreground mask on calculating with
                the Otsu Thresholding.
            method (str, optional): Binarization method. As default, calculates
                with Otsu Thresholding.
            min (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
            max (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
        """
        self.base_masks(slide.wsi_height, slide.wsi_width)
        self.main_masks()
        if foreground:
            self.make_foreground_mask(
                slide, size, method=foreground, min_=min_, max_=max_)
        if rule:
            self.classes = list(set(self.classes) & set(rule.classes))
            self.include_masks(rule)
            self.merge_include_coords(rule)
            self.exclude_masks(rule)
            # self.exclude_coords(rule)

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
            contours = np.array(self.mask_coords[cls], dtype=object)
            for contour in contours:
                self.masks[cls] = cv2.drawContours(
                    self.masks[cls], [np.int32(contour)], 0, True,
                    thickness=cv2.FILLED)

    def include_masks(self, rule):
        """Merge masks following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        self.masks_include = self.masks.copy()
        for cls in self.classes:
            if not hasattr(rule, cls):
                continue
            for include in getattr(rule, cls)["includes"]:
                if include not in self.masks:
                    continue
                self.masks_include[cls] = cv2.bitwise_or(
                    self.masks[cls], self.masks[include])
        self.masks = self.masks_include

    def merge_include_coords(self, rule):
        """Merge coordinations following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        for cls in self.classes:
            if not hasattr(rule, cls):
                continue
            for include in getattr(rule, cls)["includes"]:
                if include not in self.mask_coords.keys():
                    continue
                self.mask_coords[cls].extend(self.mask_coords[include])

    def exclude_masks(self, rule):
        """Exclude area from base mask with following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        self.masks_exclude = self.masks.copy()
        for cls in self.classes:
            if not hasattr(rule, cls):
                continue
            for exclude in getattr(rule, cls)["excludes"]:
                if exclude not in self.masks:
                    continue
                overlap_area = cv2.bitwise_and(
                    self.masks[cls], self.masks[exclude])
                self.masks_exclude[cls] = cv2.bitwise_xor(
                    self.masks_exclude[cls], overlap_area)
        self.masks = self.masks_exclude

    def exclude_coords(self, rule):
        """Exclude coordinations following the rule.

        Args:
            rule (wsiprocess.rule.Rule): Rule object.
        """
        for cls in self.classes:
            if not hasattr(rule, cls):
                continue
            base_set = [tuple(c) for c in self.mask_coords[cls]]
            for exclude in getattr(rule, cls)["excludes"]:
                exclude_set = [tuple(c) for c in self.mask_coords[exclude]]
                base_set -= exclude_set
            self.mask_coords[cls] = [list(c) for c in base_set]

    def make_foreground_mask(
            self, slide, size=2000, method="otsu", min_=30, max_=190):
        """Make foreground mask.

        With otsu thresholding, make simple foreground mask.

        Args:
            slide (wsiprocess.slide.Slide): Slide object.
            size (int, or function, optional): Size of foreground mask on
                calculating with the Otsu Thresholding.
            method (str, optional): Binarization method. As default, calculates
                with Otsu Thresholding.
            min (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
            max (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
        """
        if "foreground" in self.classes:
            return
        thumb = slide.get_thumbnail(size)
        thumb = np.ndarray(
            buffer=thumb.write_to_memory(),
            dtype=np.uint8,
            shape=[thumb.height, thumb.width, thumb.bands])
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        if method == "minmax":
            mask = self._minmax_mask(thumb_gray, min_, max_)
        elif callable(method):
            mask = method(thumb_gray)
        else:
            mask = self._otsu_method_mask(thumb_gray)
        self.masks["foreground"] = cv2.resize(mask, (slide.width,
                                                     slide.height))
        self.classes.append("foreground")

    def _otsu_method_mask(self, thumb_gray):
        """Make mask of foreground with Otsu's method.

        Foreground as 1, background as 0.

        Args:
            thumb_gray (numpy.ndarray): Mask image from 0 to 255.

        Returns:
            mask (numpy.ndarray): Binary mask image.
        """
        _, mask = cv2.threshold(
            thumb_gray, 0, 1, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        return mask

    def _minmax_mask(self, thumb_gray, min_, max_):
        """Make mask of foreground from min and max value.

        Pixels with value between min_ and max_ is converted to 1 as
        foreground, and value less than min_ and more than max_ is converted to
        0 as background.

        Args:
            thumb_gray (numpy.ndarray): Mask image from 0 to 255.
            min_ (int): Minimum value of thumb_gray to convert to 1.
            max_ (int): Maximum value of thumb_gray to convert to 1.

        Returns:
            mask (numpy.ndarray): Binary mask image.
        """
        mask = ((min_ <= thumb_gray) & (thumb_gray <= max_)).astype(np.uint8)
        return mask

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
        cv2.imwrite(
            str(Path(save_to)/"{}.png".format(cls)),
            self.masks[cls], (cv2.IMWRITE_PXM_BINARY, 1))
