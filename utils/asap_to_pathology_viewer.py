from lxml import etree
import numpy as np
import argparse
from pathlib import Path
import json
import openslide


class AnnotationParser:

    def __init__(self, path):
        self.path = path
        tree = etree.parse(self.path)
        self.annotations = tree.xpath("/ASAP_Annotations/Annotations/Annotation")
        self.annotation_groups = tree.xpath("/ASAP_Annotations/AnnotationGroups/Group")
        self.classes = [group.attrib["Name"] for group in self.annotation_groups]
        self.mask_coords = {}
        for cls in self.classes:
            self.mask_coords[cls] = []
        self.read_mask_coords()

    def read_mask_coords(self):
        for cls in self.classes:
            self.read_mask_coord(cls)

    def read_mask_coord(self, cls):
        for annotation in self.annotations:
            if annotation.attrib["PartOfGroup"] == cls:
                contour = []
                for coord in annotation.xpath("Coordinates/Coordinate"):
                    x = np.float(coord.attrib["X"])
                    y = np.float(coord.attrib["Y"])
                    contour.append([round(float(x)), round(float(y))])
                self.mask_coords[cls].append(contour)


def to_pathology_viewer(parser):
    data = {}
    filename = Path(parser.path).stem + ".ndpi"
    data[filename] = {}
    data[filename]["folder"] = str(Path(parser.path).parent)

    data[filename]["source"] = {}
    data[filename]["source"]["database"] = ""
    data[filename]["source"]["annotation"] = "pathology_viewer"
    data[filename]["source"]["image"] = "Whole Slide Image"
    data[filename]["source"]["flickrid"] = ""

    data[filename]["owner"] = {}
    data[filename]["owner"]["flickrid"] = ""
    data[filename]["owner"]["name"] = ""

    wsi = openslide.OpenSlide(str(data[filename]["folder"] + "/" + filename))
    data[filename]["size"] = {}
    data[filename]["size"]["width"] = wsi.dimensions[0]
    data[filename]["size"]["height"] = wsi.dimensions[1]

    data[filename]["segmented"] = ""

    data[filename]["classes"] = parser.classes

    data[filename]["object"] = []

    for cls in parser.classes:
        for pts in parser.mask_coords[cls]:
            obj = {}
            obj["name"] = cls
            obj["pose"] = ""
            obj["truncated"] = ""
            obj["difficult"] = ""
            obj["annotator"] = "human"
            if shape_is_rectangle(pts):
                obj["bndbox"] = {}
                obj["bndbox"]["xmin"] = min(map(float, [pts[0][0], pts[1][0], pts[2][0], pts[3][0]]))
                obj["bndbox"]["xmax"] = max(map(float, [pts[0][0], pts[1][0], pts[2][0], pts[3][0]]))
                obj["bndbox"]["ymin"] = min(map(float, [pts[0][1], pts[1][1], pts[2][1], pts[3][1]]))
                obj["bndbox"]["ymax"] = max(map(float, [pts[0][1], pts[1][1], pts[2][1], pts[3][1]]))
            else:
                obj["bndbox"] = []
                for pt in pts:
                    obj["bndbox"].append({"x": pt[0],
                                          "y": pt[1]})
            data[filename]["object"].append(obj)

    return data


def shape_is_rectangle(pts):
    x0, y0 = map(float, pts[0])
    x1, y1 = map(float, pts[1])
    x2, y2 = map(float, pts[2])
    x3, y3 = map(float, pts[3])

    xc = (x0 + x1 + x2 + x3) / 4
    yc = (y0 + y1 + y2 + y3) / 4
    d0 = abs(xc-x0) + abs(yc-y0)
    d1 = abs(xc-x1) + abs(yc-y1)
    d2 = abs(xc-x2) + abs(yc-y2)
    d3 = abs(xc-x3) + abs(yc-y3)

    return d0 == d1 == d2 == d3


def save_data(data, save_to=False):
    filename = list(data.keys())[0]
    if save_to:
        folder = save_to
    else:
        folder = data[filename]["folder"]
    save_as = str(Path(folder)/Path(filename).stem) + ".json"

    with open(save_as, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("xmldata")
    argparser.add_argument("-s", "--save_to", default=False)
    args = argparser.parse_args()

    parser = AnnotationParser(args.xmldata)
    data = to_pathology_viewer(parser)

    save_data(data, args.save_to)


if __name__ == '__main__':
    main()
