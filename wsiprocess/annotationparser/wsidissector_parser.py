# -*- coding: utf-8 -*-

import json


class AnnotationParser:
    """Annotation parser for WSIDissector

    Args:
        path (str): Path to the annotation file.

    Attributes:
        path (str): Path to the annotation file.
        annotation (dict): Annotation data loaded as json file.
        filename (str): Name of the targeted whole slide image file.
        classes (list): List of the names of the classes.
        mask_coords (dict): Coordinates of the masks.
    """

    def __init__(self, path):
        self.path = path
        with open(self.path, "r") as f:
            self.annotation = json.load(f)
        self.filename = self.annotation["slide"]
        self.classes = self.annotation["classes"]
        self.mask_coords = {}
        for cls in self.classes:
            self.mask_coords[cls] = []
        self.read_mask_coords()

    def read_mask_coords(self):
        """Parse the coordinates of masks.

        """
        annotations = self.annotation["result"]
        for annotation in annotations:
            cls = annotation["class"]
            contour = []
            if "points" in annotation:
                for point in annotation["points"]:
                    contour.append([point["x"], point["y"]])
            else:
                x = round(annotation["x"])
                y = round(annotation["y"])
                w = round(annotation["w"])
                h = round(annotation["h"])
                contour.append([x, y])
                contour.append([x+w, y])
                contour.append([x+w, y+h])
                contour.append([x, y+h])
            self.mask_coords[cls].append(contour)
