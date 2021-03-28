import json
from collections import defaultdict
from wsiprocess.error import AnnotationLabelError

from .parser_utils import BaseParser


class QuPathAnnotation(BaseParser):
    """Annotation Parser for QuPath.

    Args:
        path (str): Path to the annotation file.

    Attributes:
        path (str): Path to the annotation file.
        annotations (list): List of etree Elements.
        classes (list): List of classes defined with QuPath.
        mask_coords (dict): Coordinates of the masks.
    """

    def __init__(self, path):
        super().__init__(path)

        with open(path, "r") as f:
            self.annotations = json.load(f)
        self.mask_coords = defaultdict(list)

        self.read_classes()
        self.read_coordinates()

    def read_classes(self):
        classes = list()
        for annotation in self.annotations:
            if "classification" not in annotation["properties"]:
                raise AnnotationLabelError("Some annotations have no label.")
            classes.append(annotation["properties"]["classification"]["name"])
        self.classes = list(set(classes))

    def read_coordinates(self):
        """Parse the coordinates of the mask.
        """
        for annotation in self.annotations:
            cls = annotation["properties"]["classification"]["name"]
            annotation_type = annotation["geometry"]["type"]

            if annotation_type in ["Polygon"]:
                coordinates = annotation["geometry"]["coordinates"][0]

            elif annotation_type in ["LineString"]:
                coordinates = annotation["geometry"]["coordinates"]

            else:
                raise NotImplementedError(f"Unknown type {annotation_type}")

            coordinates = self.all_as_int(coordinates)
            self.mask_coords[cls].append(coordinates)

    def all_as_int(self, points):
        int_points = [[round(point[0]), round(point[1])] for point in points]
        return int_points
