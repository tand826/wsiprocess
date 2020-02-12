import json


class AnnotationParser:

    def __init__(self, path):
        self.path = path
        with open(self.path, "r") as f:
            self.annotation = json.load(f)
        self.filename = list(self.annotation.keys())[0]
        self.classes = self.annotation[self.filename]["classes"]
        self.mask_coords = {}
        for cls in self.classes:
            self.mask_coords[cls] = []
        self.read_mask_coords()

    def read_mask_coords(self):
        boxes = self.annotation[self.filename]["object"]
        for box in boxes:
            cls = box["name"]
            coords = box["bndbox"]
            contour = []
            if isinstance(coords, dict):
                xmin = round(float(coords["xmin"]))
                ymin = round(float(coords["ymin"]))
                xmax = round(float(coords["xmax"]))
                ymax = round(float(coords["ymax"]))
                contour.append([xmin, ymin])
                contour.append([xmin, ymax])
                contour.append([xmax, ymax])
                contour.append([xmax, ymin])
            elif isinstance(coords, list):
                for coord in coords:
                    x = round(float(coord["x"]))
                    y = round(float(coord["y"]))
                    contour.append([x, y])
            self.mask_coords[cls].append(contour)
