from lxml import etree


def detect_type(path):
    try:
        tree = etree.parse(path)
        root = tree.getroot()
        if root.tag == "ASAP_Annotations":
            return "ASAP"
    except:
        return "Unknown"
