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
from typing import Callable
import warnings
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

import psutil
import cv2
import numpy as np
import wsiprocess.annotationparser as parsers
from .annotationparser.parser_utils import detect_type


class Annotation:

    def __init__(self, path, is_image=False, slidename=False):
        """Initialize the anntation object.

        Args:
            path(str): Path to the anntation data.
                Text data made with "WSIDissector" or "ASAP", and Image data
                (non-pyramidical) are available.
            is_image(bool): Whether the image is image.

        Attributes:
            low_memory_consumption (bool): If true, annotaion object does not
                keep the processed masks on the ram, and read the area from
                disk when called get_patch.
        """
        self.path = path
        self.slidename = slidename
        self.dot_bbox_width = self.dot_bbox_height = False
        self.is_image = is_image
        self.low_memory_consumption = False
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
            parsed = parsers.ASAPAnnotation(self.path)
        elif annotation_type == "WSIDissector":
            parsed = parsers.WSIDissectorAnnotation(self.path)
        elif annotation_type == "SlideRunner":
            parsed = parsers.SlideRunnerAnnotation(self.path, self.slidename)
        elif annotation_type == "QuPath":
            parsed = parsers.QuPathAnnotation(self.path)
        elif annotation_type == "Empty":
            parsed = parsers.BaseParser(self.path)
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
            self, slide, rule=False, foreground_fn="otsu", size=5000,
            min_=30, max_=190):
        """Make masks from the slide and rule.

        Masks are for each class and foreground area.

        Args:
            slide (wsiprocess.slide.Slide): Slide object
            rule (:obj:`wsiprocess.rule.Rule`, optional): Rule object
            foreground_fn (str or callable, optional): This can be {otsu,
                minmax} or a user specified function.
            size (int, optional): Size of foreground mask.
            min (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
            max (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
        """
        if rule:
            self.classes = list(set(self.classes) & set(rule.classes))
        self.check_memory_consumption(slide.height, slide.width)
        self.set_scale(size, slide.height, slide.width)
        self.base_masks(size, slide.height, slide.width)
        self.main_masks(size, slide.height, slide.width)
        if foreground_fn:
            self.foreground_mask(
                slide, size, slide.height, slide.width, fn=foreground_fn,
                min_=min_, max_=max_)
            self.fix_mask_size()
        if rule:
            self.include_masks(rule)
            self.merge_include_coords(rule)
            self.exclude_masks(rule)
            # self.exclude_coords(rule)
        if not self.low_memory_consumption:
            self.resize_masks(slide.height, slide.width)

    def check_memory_consumption(self, wsi_height, wsi_width):
        num_classes = len(self.classes) if self.classes else 1
        total_mask_size = num_classes*(wsi_height*wsi_width+120)
        mask_is_too_large = total_mask_size > psutil.virtual_memory().available
        if mask_is_too_large:
            msg = "Full size mask is too large for the RAM. "
            msg += "Running in low memory consumption mode."
            warnings.warn(msg)
            self.low_memory_consumption = True

    def set_scale(self, size, wsi_height, wsi_width):
        self.scale = self.get_scale(size, wsi_height, wsi_width)

    def get_scale(self, size, wsi_height, wsi_width):
        return size / max(wsi_height, wsi_width)

    def base_masks(self, size, wsi_height, wsi_width):
        """Make base masks.

        Args:
            size (int): The long side of masks.
            wsi_height (int): The height of wsi.
            wsi_width (int): The width of wsi.
        """
        scale = self.get_scale(size, wsi_height, wsi_width)
        mask_height = self._round(str(wsi_height * scale))
        mask_width = self._round(str(wsi_width * scale))

        for cls in self.classes:
            self.base_mask(cls, mask_height, mask_width)

    def _round(self, num):
        num = str(num)
        return int(Decimal(num).quantize(Decimal('0'), rounding=ROUND_HALF_UP))

    def base_mask(self, cls, mask_height, mask_width):
        """ Masks have same size of as the slide.

        Masks are canvases of 0s.

        Args:
            cls (str): Class name for each mask.
            mask_height (int): The height of base masks.
            mask_width (int): The width of base masks.
        """
        self.masks[cls] = np.zeros((mask_height, mask_width), dtype=np.uint8)

    def main_masks(self, size, wsi_height, wsi_width):
        """Main masks

        Write border lines following the rule and fill inside with 255.
        """

        scale = self.get_scale(size, wsi_height, wsi_width)
        for cls in self.classes:
            self.main_mask(cls, scale)

    def main_mask(self, cls, scale):
        contours = np.array(self.mask_coords[cls], dtype=object)
        for contour in contours:
            self.masks[cls] = cv2.drawContours(
                self.masks[cls],
                [np.int32(np.array(contour)*scale)], 0, 1,
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

    def foreground_mask(
            self, slide, size=5000, wsi_height=False, wsi_width=False,
            fn="otsu", min_=30, max_=190):
        """Make foreground mask.

        With otsu thresholding, make simple foreground mask.

        Args:
            slide (wsiprocess.slide.Slide): Slide object.
            size (int, or function, optional): Size of foreground mask on
                calculating with the Otsu Thresholding.
            wsi_width (int or bool): Width of the wsi.
            wsi_height (int or bool): Height of the wsi.
            fn (str or function, optional): Binarization method. As default,
                calculates with Otsu Thresholding.
            min (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
            max (int, optional): Used if method is "minmax". Annotation object
                defines foreground as the pixels with the value between "min"
                and "max".
        """
        if "foreground" in self.classes:
            print("foreground is already calculated.")
            return

        if wsi_width and wsi_height:
            scale = self.get_scale(size, wsi_height, wsi_width)
            thumb_height = self._round(str(wsi_height * scale))
            thumb_width = self._round(str(wsi_width * scale))
            thumb_size = (thumb_width, thumb_height)
        else:
            thumb_size = size

        thumb = np.asarray(slide.get_thumbnail(thumb_size))
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        if isinstance(fn, str):
            if fn == "minmax":
                mask = self._minmax_mask(thumb_gray, min_, max_)
            elif fn == "otsu":
                mask = self._otsu_method_mask(thumb_gray)
            else:
                raise NotImplementedError(
                    "{} is not implemented for making masks.".format(fn))
        elif isinstance(fn, Callable):
            mask = fn(thumb_gray)
        else:
            raise NotImplementedError(
                "{} is not implemented for making masks.".format(fn))
        self.masks["foreground"] = mask
        self.classes.append("foreground")

    def fix_mask_size(self):
        if "foreground" not in self.masks:
            warnings.warn("foreground mask is not set yet.")
            return

        classes = self.classes.copy()
        classes.remove("foreground")
        height, width = self.masks[classes[0]].shape
        if self.masks["foreground"].shape != (height, width):
            self.masks["foreground"] = cv2.resize(self.masks["foreground"], (width, height))

    def resize_masks(self, wsi_height, wsi_width):
        """Resize the masks as the same size as the slide

        Args:
            slide (wsiprocess.slide.Slide): Slide object.
        """
        for cls in self.classes:
            self.resize_mask(wsi_height, wsi_width, cls)

    def resize_mask(self, wsi_height, wsi_width, cls):
        """Resize a mask as the same size as the slide"""

        self.masks[cls] = cv2.resize(
            self.masks[cls], (wsi_width, wsi_height))

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
        scale = self.get_scale(size, height, width)
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

    def get_patch_mask(self, cls, x, y, w, h):
        if self.low_memory_consumption:
            x_ = int(x * self.scale)
            y_ = int(y * self.scale)
            w_ = int(w * self.scale)
            h_ = int(h * self.scale)
            patch_mask = self.masks[cls][y_:y_+h_, x_:x_+w_]
            return cv2.resize(patch_mask, dsize=(w, h))

        else:
            return self.masks[cls][y:y+h, x:x+w]
