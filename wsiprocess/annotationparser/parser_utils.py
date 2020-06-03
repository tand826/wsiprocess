# -*- coding: utf-8 -*-
from pathlib import Path
from lxml import etree
import json


def detect_type(path):
    """Detect the type of input file.

    Returns:
        (str): One of {"ASAP", "pathology_viewe, "Empty"}
    """
    if Path(path).suffix == ".xml":
        tree = etree.parse(path)
        root = tree.getroot()
        if root.tag == "ASAP_Annotations":
            return "ASAP"
    elif Path(path).suffix == ".json":
        with open(path, "r") as f:
            data = json.load(f)
        if data["annotationTool"] == "WSIDissector":
            return "WSIDissector"
    return "Empty"
