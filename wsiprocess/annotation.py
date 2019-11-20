from lxml import etree
import cv2
import numpy as np


class Annotation:

    def __init__(self, path):
        self.path = path
        self.read_annotation()

    def read_annotation(self):
        tree = etree.parse(self.path)
        self.annots = tree.xpath("/ASAP_Annotations/Annotations/Annotation")
        self.annot_grps = tree.xpath("/ASAP_Annotations/AnnotationGroups/Group")
        self.clses = [grp.attrib["Name"] for grp in self.annot_grps]
        assert len(self.annots) > 0, "No annotations found."

    def to_mask(self, wsi_height, wsi_width, inclusion=False):
        self.base_mask(self, wsi_height, wsi_width)
        self.main_mask(self)
        if inclusion:
            self.exclude_mask(self, inclusion)

    def base_mask(self, wsi_height, wsi_width):
        self.masks = {}
        for cls in self.clses:
            self.masks[cls] = np.zeros((wsi_height, wsi_width), dtype=np.uint8)

    def main_mask(self):
        for annot in self.annots:
            cls = annot.attrib["PartOfGroup"]
            contour = []
            for coord in annot.xpath("Coordinates/Coordinate"):
                x = np.float(coord.attrib["X"])
                y = np.float(coord.attrib["Y"])
                contour.append([[x, y]])
            contour = np.concatenate(contour).astype(np.int32)
            self.masks[cls] = cv2.drawContours(self.masks[cls], [contour], 0, True, thickness=cv2.FILLED)

    def exclude_mask(self, inclusion):
        self.masks_exclude = self.masks.copy()
        for cls in self.clses:
            for excludes in getattr(inclusion, cls):
                for exclude in excludes:
                    overlap_area = cv2.bitwise_and(self.masks[cls], self.mask[exclude])
                    self.masks_exclude[cls] = cv2.bitwise_xor(self.masks[cls], overlap_area)
        self.masks = self.masks_exclude

    def foreground_mask(self, slide, args, size=2000, save_as=False):
        thumb = slide.slide.thumbnail_image(size, height=size)
        thumb = np.array(buffer=thumb.write_to_memory(), dtype=np.uint8, shape=[thumb.height, thumb.width, thumb.bands])
        thumb_gray = cv2.cvtColor(thumb, cv2.COLOR_RGB2GRAY)
        _, th = cv2.threshold(thumb_gray, 0, 1, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        scale = max(size / slide.wsi_width, size / slide.wsi_height)
        self.masks["foreground"] = cv2.resize(th, dsize=None, fx=scale, fy=scale)
        if save_as:
            cv2.imwrite(str(args.output_dir/"masks"/"{}_fg.png".format(args.wsi.stem)), self.masks["foreground"], (cv2.IMWRITE_PXM_BINARY, 1))

    def export_mask_thumb(self, args, size=512):
        for cls, mask in self.masks.items():
            height, width = mask.shape
            scale = max(size / height, size / width)
            mask_resized = cv2.resize(mask, dsize=None, fx=scale, fy=scale)
            mask_scaled = mask_resized * 255
            cv2.imwrite(str(args.output_dir/"masks"/"{}_thumb.png".format(cls)), mask_scaled)

    def export_mask(self, args):
        for cls, mask in self.masks.items():
            cv2.imwrite(str(args.output_dir/"masks"/"{}.png".format(cls)), mask, (cv2.IMWRITE_PXM_BINARY, 1))
