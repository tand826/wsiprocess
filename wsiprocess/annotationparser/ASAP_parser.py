# -*- coding: utf-8 -*-
from pathlib import Path
from lxml import etree
import numpy as np


class AnnotationParser:
    """Annotation Parser for ASAP.

    Args:
        path (str): Path to the annotation file.

    Attributes:
        path (str): Path to the annotation file.
        annotations (list): List of etree Elements.
        annotation_groups (list): List of etree Elements.
        classes (list): List of classes defined with ASAP.
        mask_coords (dict): Coordinates of the masks.
    """

    def __init__(self, path):
        self.path = path
        assert Path(self.path).exists(), "This annotation file does not exist."

        tree = etree.parse(self.path)
        self.annotations = tree.xpath("/ASAP_Annotations/Annotations/Annotation")
        self.annotation_groups = tree.xpath("/ASAP_Annotations/AnnotationGroups/Group")
        self.classes = [group.attrib["Name"] for group in self.annotation_groups]
        self.mask_coords = {}
        for cls in self.classes:
            self.mask_coords[cls] = []
        self.read_mask_coords()

    def read_mask_coords(self):
        """Parse coordinates of of the masks of all classes.
        """
        for cls in self.classes:
            self.read_mask_coord(cls)

    def read_mask_coord(self, cls):
        """Parse the coordinates of the mask.

        Args:
            cls (str): Target annotation class name.
        """
        for annotation in self.annotations:
            if annotation.attrib["PartOfGroup"] == cls:
                contour = []
                for coord in annotation.xpath("Coordinates/Coordinate"):
                    x = np.float(coord.attrib["X"])
                    y = np.float(coord.attrib["Y"])
                    contour.append([round(float(x)), round(float(y))])
                self.mask_coords[cls].append(contour)
