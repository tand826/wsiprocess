# -*- coding: utf-8 -*-
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

    def __init__(self, path, slidename=False):
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
        query = "select uid, name from Classes"
        self.cursor.execute(query)
        self.classes = list()
        self.uid2cls = dict()
        for uid, name in self.cursor.fetchall():
            self.classes.append(name)
            self.uid2cls[uid] = name

    def read_slides(self):
        self.cursor.execute("select uid, filename from Slides")
        self.slidename2uid = {
            filename: uid
            for uid, filename in self.cursor.fetchall()
        }

    def read_annotations(self, slidename):
        query = "select uid, type, agreedClass from Annotations"
        if slidename:
            query += f" where slide=='{self.slidename2uid[slidename]}'"
        self.cursor.execute(query)
        self.annotations = {
            uid: {"type": annoType, "class": cls}
            for uid, annoType, cls in self.cursor.fetchall()
        }

    def read_labels(self):
        query = "select class, annoId from Annotations_label"
        self.cursor.execute(query)
        self.labels = {
            annoId: cls
            for cls, annoId in self.cursor.fetchall()
        }

    def read_coordinates(self, slidename):
        query = "select coordinateX, coordinateY, annoId, orderIdx"
        query += " from Annotations_coordinates"
        if slidename:
            query += f" where slide=='{self.slidename2uid[slidename]}'"
        self.cursor.execute(query)
        self.coordinates = defaultdict(dict)
        for x, y, annoId, order in self.cursor.fetchall():
            self.coordinates[annoId][order] = {"x": x, "y": y}

    def verify_annotations(self):
        annotation_counts = len(self.annotations)
        if not len(self.labels) == len(self.coordinates) == annotation_counts:
            raise AnnotationLabelError("Some annotations have no label.")

    def parse_mask_coords(self):
        """Parse the coordinates of the mask.
        """
        for annoId, value in self.coordinates.items():
            cls = self.uid2cls[self.labels[annoId]]

            if self.annotations[annoId]["type"] in [1, 2, 3, 4]:
                # type1 is dot annotation
                # type2 is rectangle annotation with lefttop and rightbottom
                # type3 is polygon annotation or magicwand annotation.
                # type4 is important position annotation with a dot.
                # type5 is circle anntoation.
                coordinate = [
                    [coord["x"], coord["y"]]
                    for order, coord in value.items()
                ]
                self.mask_coords[cls].append(coordinate)

            elif self.annotations[annoId]["type"] == 5:
                # type5 is circle anntoation.
                pass

            else:
                raise NotImplementedError("Unknown annotation type")
