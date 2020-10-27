# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict
import sqlite3
from pathlib import Path
from wsiprocess.error import AnnotationLabelError


class AnnotationParser:
    """Annotation Parser for SlideRunner v1.31.0

    Args:
        path (str): Path to the annotation file.

    Attributes:
        path (str): Path to the annotation file.
        classes (list): List of classes defined with ASAP.
        mask_coords (dict): Coordinates of the masks.
    """

    def __init__(self, path, slidename):
        self.path = path
        assert Path(self.path).exists(), "This annotation file does not exist."

        self.mask_coords = defaultdict(list)

        with sqlite3.connect(path) as con:
            self.cursor = con.cursor()

            self.read_classes()
            self.read_slides()
            self.read_annotations(slidename)
            self.read_labels()
            self.read_coordinates(slidename)

        self.verify_annotations()
        self.parse_mask_coords()

    def read_classes(self):
        """Read classes from Classes table.
        """
        query = "select uid, name from Classes"
        self.cursor.execute(query)
        self.classes = list()
        self.uid2cls = dict()
        for uid, name in self.cursor.fetchall():
            self.classes.append(name)
            self.uid2cls[uid] = name

    def read_slides(self):
        """Read slides from Slides table.
        A slide has unique ID and filename.
        """
        self.cursor.execute("select uid, filename from Slides")
        self.slidename2uid = {
            filename: uid
            for uid, filename in self.cursor.fetchall()
        }

    def read_annotations(self, slidename):
        """Read annotations from Annotations table.

        A annotation has unique ID, Annotation Type, and Class.

        Args:
            slidename (str): Name of the slide to filter the data.
        """
        query = "select uid, type, agreedClass from Annotations"
        query += f" where slide=='{self.slidename2uid[slidename]}'"
        self.cursor.execute(query)
        self.annotations = {
            uid: {"type": annoType, "class": cls}
            for uid, annoType, cls in self.cursor.fetchall()
        }

    def read_labels(self):
        """Read labels from Annotations_label table.

        A label has Annotation ID (sharing with Annotations), and Class.
        """
        query = "select class, annoId from Annotations_label"
        self.cursor.execute(query)
        self.labels = {
            annoId: cls
            for cls, annoId in self.cursor.fetchall()
        }

    def read_coordinates(self, slidename):
        """Read coordinates from Annotations_coordinates table.

        A coordinate has coordinate of x and y, Annotation ID and the order
        of the coordinate.

        Args:
            slidename (str): Name of the slide to filter the data.
        """
        query = "select coordinateX, coordinateY, annoId, orderIdx"
        query += " from Annotations_coordinates"
        query += f" where slide=='{self.slidename2uid[slidename]}'"
        self.cursor.execute(query)
        self.coordinates = defaultdict(dict)
        for x, y, annoId, order in self.cursor.fetchall():
            self.coordinates[annoId][order] = {"x": x, "y": y}

    def verify_annotations(self):
        """Verify the number of annotations.

        The numbers of annotations and labels and coordinates must be same.
        """
        annotation_counts = len(self.annotations)
        if not len(self.labels) == len(self.coordinates) == annotation_counts:
            raise AnnotationLabelError("Some annotations have no label.")

    def parse_mask_coords(self):
        """Parse the coordinates of the mask.

        Parse the coordinates to make a list containing lists of coordinates.
        """
        for annoId, value in self.coordinates.items():
            cls = self.uid2cls[self.labels[annoId]]

            if self.annotations[annoId]["type"] in [1, 2, 3, 4]:
                # type1 is dot annotation
                # type2 is rectangle annotation with lefttop and rightbottom
                # type3 is polygon annotation or magicwand annotation.
                # type4 is important position annotation with a dot.
                coordinate = [
                    [coord["x"], coord["y"]]
                    for order, coord in value.items()
                ]
                self.mask_coords[cls].append(coordinate)

            elif self.annotations[annoId]["type"] == 5:
                # type5 is circle anntoation.
                left = value[1]["x"]
                right = value[2]["x"]
                top = value[1]["y"]
                bottom = value[2]["y"]
                coordinate = self.bbox_to_circle(left, top, right, bottom)
                self.mask_coords[cls].append(coordinate)

            else:
                raise NotImplementedError("Unknown annotation type")

    def bbox_to_circle(self, left, top, right, bottom):
        """Convert coordinates of bounding box to circle.

        Args:
            left (int): Smaller coordinate of in the x-axis direction
            top (int): Smaller coordinate of in the y-axis direction
            right (int): Larger coordinate of in the x-axis direction
            bottom (int): Larger coordinate of in the y-axis direction

        Returns:
            coordinate (list(list)): List of list which contains one
                coordinate representing a circle in coordinates.
        """
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        radius = np.abs((right - left) / 2)
        coordinate = [
            [
                int(center_x + np.cos(theta) * radius),
                int(center_y + np.sin(theta) * radius)
            ]
            for theta in np.linspace(0, 2*np.pi, int(radius*2))
        ]
        return coordinate
