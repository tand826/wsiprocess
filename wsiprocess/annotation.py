from lxml import etree
import cv2
import numpy as np
from pathlib import Path


class Annotation:

    def __init__(self, path):
        self.path = path
        self.read_annotation()
        self.masks = {}
        self.mask_coords = {}

    def read_annotation(self):
        tree = etree.parse(self.path)
        self.annotations = tree.xpath("/ASAP_Annotations/Annotations/Annotation")
        self.annotation_groups = tree.xpath("/ASAP_Annotations/AnnotationGroups/Group")
        self.classes = [group.attrib["Name"] for group in self.annotation_groups]
        assert len(self.annotations) > 0, "No annotations found."

    def make_masks(self, slide, inclusion=False, foreground=False, size=2000):
        self.base_masks(slide.wsi_height, slide.wsi_width)
        self.main_masks()
        if inclusion:
            self.exclude_mask(inclusion)
        if foreground:
            self.make_foreground_mask(slide, size)

    def base_masks(self, wsi_height, wsi_width):
        for cls in self.classes:
            self.masks[cls] = np.zeros((wsi_height, wsi_width), dtype=np.uint8)

    def main_masks(self):
        self.mask_coords = []
        for annotation in self.annotations:
            cls = annotation.attrib["PartOfGroup"]
            contour = []
            for coord in annotation.xpath("Coordinates/Coordinate"):
                x = np.float(coord.attrib["X"])
                y = np.float(coord.attrib["Y"])
                contour.append([[x, y]])
            contours = np.concatenate(contour).astype(np.int32)
            self.masks[cls] = cv2.drawContours(self.masks[cls], contours, 0, True, thickness=cv2.FILLED)
            self.mask_coords[cls] = contours

    def exclude_masks(self, inclusion):
        self.masks_exclude = self.masks.copy()
        for cls in self.classes:
            if hasattr(inclusion, cls):
                for exclude in getattr(inclusion, cls):
                    overlap_area = cv2.bitwise_and(self.masks[cls], self.masks[exclude])
                    self.masks_exclude[cls] = cv2.bitwise_xor(self.masks[cls], overlap_area)
        self.masks = self.masks_exclude

    def make_foreground_mask(self, slide, size=2000):
        thumb = slide.slide.thumbnail_image(size, height=size)
        thumb = np.ndarray(buffer=thumb.write_to_memory(), dtype=np.uint8, shape=[thumb.height, thumb.width, thumb.bands])
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        _, th = cv2.threshold(thumb_gray, 0, 1, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        self.masks["foreground"] = cv2.resize(th, (slide.width, slide.height))
        self.classes.append("foreground")

    def export_thumb_masks(self, save_to, size=512):
        for cls in self.masks.keys():
            self.export_thumb_mask(cls, save_to, size)

    def export_thumb_mask(self, cls, save_to, size=512):
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
        cv2.imwrite(str(Path(save_to)/"{}.png".format(cls)), self.masks[cls], (cv2.IMWRITE_PXM_BINARY, 1))
