# -*- coding: utf-8 -*-
from lxml import etree
import json


def detect_type(path):
    """Detect the type of input file.

    Returns:
        (str): One of {"ASAP", "pathology_viewe, "Empty"}
    """
    try:
        tree = etree.parse(path)
        root = tree.getroot()
        if root.tag == "ASAP_Annotations":
            return "ASAP"
    except json.decoder.JSONDecodeError:
        with open(path, "r") as f:
            data = json.load(f)
        key = list(data.keys())[0]
        if data[key]["source"]["annotation"] == "pathology_viewer":
            return "pathology_viewer"
    except etree.XMLSyntaxError:
        return "Empty"
