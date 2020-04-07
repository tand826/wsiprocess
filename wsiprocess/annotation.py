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

    def read_annotation(self, annotation_type=False):
        annotation_type = detect_type(self.path)
        if annotation_type == "ASAP":
            from .annotationparser.ASAP_parser import AnnotationParser
            parsed = AnnotationParser(self.path)
        elif annotation_type == "pathology_viewer":
            from .annotationparser.pathology_viewer_parser import AnnotationParser
            parsed = AnnotationParser(self.path)
        elif annotation_type == "None":
            class Parsed:
                classes = []
                mask_coords = {}
            parsed = Parsed()
        self.classes = parsed.classes
        self.mask_coords = parsed.mask_coords

    def make_masks(self, slide, rule=False, foreground=False, size=2000):
        self.base_masks(slide.wsi_height, slide.wsi_width)
        self.main_masks()
        if rule:
            self.classes = list(set(self.classes) & set(rule.classes))
            self.include_masks(rule)
            self.exclude_masks(rule)
        if foreground:
            self.make_foreground_mask(slide, size)

    def base_masks(self, wsi_height, wsi_width):
        for cls in self.classes:
            self.base_mask(cls, wsi_height, wsi_width)

    def base_mask(self, cls, wsi_height, wsi_width):
        self.masks[cls] = np.zeros((wsi_height, wsi_width), dtype=np.uint8)

    def main_masks(self):
        for cls in self.classes:
            contours = np.array(self.mask_coords[cls])
            for contour in contours:
                self.masks[cls] = cv2.drawContours(
                    self.masks[cls], [np.int32(contour)], 0, True, thickness=cv2.FILLED)

    def include_masks(self, rule):
        self.masks_include = self.masks.copy()
        for cls in self.classes:
            if hasattr(rule, cls):
                print(rule)
                for include in getattr(rule, cls)["includes"]:
                    if include in self.masks:
                        self.masks_include[cls] = cv2.bitwise_or(
                            self.masks[cls], self.masks[include])
        self.masks = self.masks_include

    def exclude_masks(self, rule):
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
        if "foreground" in self.classes:
            return
        thumb = slide.get_thumbnail(size)
        thumb = np.ndarray(buffer=thumb.write_to_memory(), dtype=np.uint8, shape=[
                           thumb.height, thumb.width, thumb.bands])
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        _, th = cv2.threshold(
            thumb_gray, 0, 1, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        self.masks["foreground"] = cv2.resize(th, (slide.width, slide.height))
        self.classes.append("foreground")

    def export_thumb_masks(self, save_to=".", size=512):
        for cls in self.masks.keys():
            self.export_thumb_mask(cls, save_to, size)

    def export_thumb_mask(self, cls, save_to=".", size=512):
        mask = self.masks[cls]
        height, width = mask.shape
        scale = max(size / height, size / width)
        mask_resized = cv2.resize(mask, dsize=None, fx=scale, fy=scale)
        mask_scaled = mask_resized * 255
        cv2.imwrite(str(Path(save_to)/"{}_thumb.png".format(cls)), mask_scaled)

    def export_masks(self, save_to):
        for cls in self.masks.keys():
            self.export_mask(save_to, cls)

    def export_mask(self, save_to, cls):
        cv2.imwrite(str(Path(save_to)/"{}.png".format(cls)),
                    self.masks[cls], (cv2.IMWRITE_PXM_BINARY, 1))
