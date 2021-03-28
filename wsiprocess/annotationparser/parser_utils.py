# -*- coding: utf-8 -*-
from pathlib import Path
from lxml import etree
import json
import sqlite3


def detect_type(path):
    """Detect the type of input file.

    Returns:
        file_type (str): One of {"ASAP", "WSIDissector", "SlideRunner",
            "WSIDissector", "Empty"}
    """
    path = Path(path)
    if path.suffix == ".xml":
        tree = etree.parse(str(path))
        root = tree.getroot()
        if root.tag == "ASAP_Annotations":
            return "ASAP"
    elif path.suffix == ".json":
        with open(path, "r") as f:
            data = json.load(f)
        if "annotationTool" in data:
            if data["annotationTool"] == "WSIDissector":
                return "WSIDissector"
        elif data[0].keys() >= {"type", "id", "geometry", "properties"}:
            return "QuPath"
    elif path.suffix == ".sqlite":
        try:
            con = sqlite3.connect(path)
            cursor = con.cursor()
            cursor.execute("select * from sqlite_sequence")
            assumed = set([
                "Persons", "Classes", "Slides", "Annotations",
                "Annotations_coordinates", "Annotations_label", "Log"])
            if assumed == set([x[0] for x in cursor.fetchall()]):
                file_type = "SlideRunner"
        except Exception as e:
            print(e)
    else:
        file_type = "Empty"
    return file_type


class BaseParser:
    """Base class for Parsers"""

    def __init__(self, path):
        """
        Args:
            path (str): Path to the annotation file.
        Attributes:
            path (str): Path to the annotation file.
        """
        self.path = path
        assert Path(self.path).exists(), "This annotation file does not exist."

        self.classes = []
        self.mask_coords = {}
