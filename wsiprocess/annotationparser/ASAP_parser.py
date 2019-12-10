from lxml import etree
import numpy as np


class AnnotationParser:

    def __init__(self, path):
        self.path = path
        tree = etree.parse(self.path)
        self.annotations = tree.xpath("/ASAP_Annotations/Annotations/Annotation")
        self.annotation_groups = tree.xpath("/ASAP_Annotations/AnnotationGroups/Group")
        self.classes = [group.attrib["Name"] for group in self.annotation_groups]
        for cls in self.classes:
            self.mask_coords[cls] = []
        self.read_mask_coords()

    def read_mask_coords(self):
        pass

    def read_mask_coord(self, cls):
        for annotation in self.annotations:
            if annotation.attrib["PartOfGroup"] == cls:
                contour = []
                for coord in annotation.xpath("Coordinates/Coordinate"):
                    x = np.float(coord.attrib["X"])
                    y = np.float(coord.attrib["Y"])
                    contour.append([round(float(x)), round(float(y))])
                self.mask_coords[cls].append(contour)
