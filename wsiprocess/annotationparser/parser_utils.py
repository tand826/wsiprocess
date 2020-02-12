from lxml import etree
import json


def detect_type(path):
    try:
        tree = etree.parse(path)
        root = tree.getroot()
        if root.tag == "ASAP_Annotations":
            return "ASAP"
    except:
        with open(path, "r") as f:
            data = json.load(f)
        key = list(data.keys())[0]
        if data[key]["source"]["annotation"] == "pathology_viewer":
            return "pathology_viewer"
