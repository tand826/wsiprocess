# -*- coding: utf-8 -*-
"""Converter to COCO style.

wsiprocess_to_coco is convert helper which convert the wsiprocess output for
COCO object detection format.
Only available for "detection" method, but works when extracting patches and
after extraction.

"""
import argparse
import shutil
import random
import json
from datetime import datetime
from pathlib import Path

import cv2


class SaveTo(type(Path())):

    def __init__(self, path):
        self.annotations = self/"annotations"
        self.train = self/"train2014"
        self.val = self/"val2014"
        self.test = self/"test2014"

        self.mkdir(exist_ok=True)
        self.annotations.mkdir(exist_ok=True)
        self.train.mkdir(exist_ok=True)
        self.val.mkdir(exist_ok=True)
        self.test.mkdir(exist_ok=True)


class ToCOCOConverter:
    """Converter class.
    """

    def __init__(self, params=False, per_wsi=False):
        if params:
            self.root = Path(params["root"])
            self.save_to = SaveTo(f"{params['save_to']}/coco")
            self.ratio_arg = params["ratio_arg"]
        else:
            self.getargs()
        self.per_wsi = per_wsi
        self.test_is_available = len(self.ratio_arg.split(":")) == 3
        self.phases = ["train", "val"]
        if self.test_is_available:
            self.phases.append("test")

        self.now = datetime.now().strftime('%Y/%m/%d_%H:%M:%S')
        self.paths = {phase: [] for phase in self.phases}
        self.get_base()
        self.get_ratio()
        self.read_annotation()
        self.set_id()

    def set_id(self):
        last_image_id, last_annotation_id = 0, 0
        for phase in self.phases[::-1]:
            target = f"instances_{phase}2014.json"
            if (self.save_to.annotations/target).exists():
                with open(self.save_to.annotations/target, "r") as f:
                    data = json.load(f)
                    try:
                        last_image_id = data["images"][-1]["id"]
                        last_annotation_id = data["annotations"][-1]["id"]
                    except IndexError:
                        continue

        self.image_id = last_image_id + 1
        self.annotation_id = last_annotation_id + 1

    def convert(self):
        self.make_link_to_images()
        self.add_info()
        self.add_categories()
        self.add_images_and_annotations()
        self.save_data()

    def getargs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "root", type=Path, help="Parent of results.json located")
        parser.add_argument("-s", "--save_to", default="./wp/coco", type=Path)
        parser.add_argument(
            "-r", "--ratio", default="8:1:1",
            help="Ratio of train and val and test ie. 8:1:1")
        args = parser.parse_args()
        self.root = args.root
        self.save_to = args.save_to
        self.ratio_arg = args.ratio

    def get_ratio(self):
        if self.per_wsi:
            self.ratio = {p: r for p, r in zip(self.phases, [0, 0, 1])}
            return
        ratios = list(map(float, self.ratio_arg.split(":")))
        self.ratio = {p: r / sum(ratios) for p, r in zip(self.phases, ratios)}

    def add_info(self):
        for phase in self.phases:
            self.coco_data[phase]["info"] = info(self.now)

    def make_link_to_images(self):
        for cls in self.annotation["classes"]:
            paths = list((self.root/"patches").glob(f"{cls}/*"))
            random.shuffle(paths)

            train_count = int(len(paths)*self.ratio["train"])
            self.paths["train"] += paths[:train_count]
            if self.test_is_available:
                val_count = int(len(paths)*self.ratio["val"])
                val_count_end = train_count + val_count
                self.paths["val"] += paths[train_count:val_count_end]
                self.paths["test"] += paths[train_count+val_count:]
            else:
                self.paths["val"] += paths[train_count:]

        for phase in self.phases:
            for image_path in self.paths[phase]:
                img_name = image_path.name
                if not (self.save_to/f"{phase}2014"/img_name).exists():
                    shutil.copy(image_path, self.save_to/f"{phase}2014")

    def get_base(self):
        self.coco_data = {}
        for phase in self.phases:
            save_to = self.save_to.annotations
            json_path = save_to/f"instances_{phase}2014.json"
            if json_path.exists():
                with open(json_path, "r") as f:
                    self.coco_data[phase] = json.load(f)
            else:
                self.coco_data[phase] = base()

    def read_annotation(self):
        with open(self.root/"results.json", "r") as f:
            self.annotation = json.load(f)

    def add_categories(self):
        for idx, cls in enumerate(self.annotation["classes"]):
            for phase in self.phases:
                self.add_category(phase, idx, cls)

    def add_images_and_annotations(self):
        if self.per_wsi:
            self.add_image("test", self.annotation["slide"])
            for path in self.paths["test"]:
                self.add_annotation("test", Path("0_0"))
            return
        for phase in self.phases:
            for path in self.paths[phase]:
                self.add_image(phase, path)
                self.add_annotation(phase, path)
                self.image_id += 1

    def add_category(self, phase, category_idx, name):
        cat = category(category_idx, name)
        if cat not in self.coco_data[phase]["categories"]:
            self.coco_data[phase]["categories"].append(cat)

    def add_image(self, phase, file_name):
        if self.per_wsi:
            width = self.annotation["wsi_width"]
            height = self.annotation["wsi_height"]
        else:
            width = self.annotation["patch_width"]
            height = self.annotation["patch_height"]
        self.coco_data[phase]["images"].append(
            image(file_name, width, height, self.image_id)
        )

    def add_annotation(self, phase, path):
        x, y = map(int, path.stem.split("_")[-2:])
        for result in self.annotation["result"]:
            if (not self.per_wsi) and (result["x"] != x or result["y"] != y):
                continue
            offsetx = x
            offsety = y
            if result.get("bbs"):
                for bb in result["bbs"]:
                    if not self.per_wsi:
                        bb["x"] %= self.annotation["patch_width"]
                        bb["y"] %= self.annotation["patch_height"]
                    self.coco_data[phase]["annotations"].append(
                        annotation(
                            bb, offsetx, offsety, self.image_id,
                            self.annotation_id, self.annotation["classes"],
                            mode="detection", per_wsi=self.per_wsi)
                    )
                    self.annotation_id += 1
            elif result.get("masks"):
                for mask in result["masks"]:
                    annotations = annotation(
                        mask, offsetx, offsety, self.image_id,
                        self.annotation_id, self.annotation["classes"],
                        mode="segmentation", per_wsi=self.per_wsi)
                    self.coco_data[phase]["annotations"].extend(annotations)
                    self.annotation_id += len(annotations)

    def save_data(self):
        for phase in self.phases:
            target = f"instances_{phase}2014.json"
            with open(self.save_to.annotations/target, "w") as f:
                json.dump(self.coco_data[phase], f, indent=4)


def base():
    return {
        "info": {},
        "licenses": [],
        "categories": [],
        "images": [],
        "annotations": []
    }


def info(now):
    return {
        "description": "wsiprocess",
        "url": "",
        "version": "1.0",
        "year": 2014,
        "contributor": "",
        "date_created": now
    }


def category(category_idx, name):
    # category_idx starts from 0 -> plus 1 to set as id
    return {
        "supercategory": "",
        "id": category_idx+1,
        "name": name}


def image(file_name, width, height, image_id):
    return {
        "license": "",
        "file_name": str(file_name),
        "coco_url": "",
        "width": width,
        "height": height,
        "date_captured": "",
        "flickr_url": "",
        "id": image_id
    }


def annotation(
        result, offsetx, offsety, image_id, annotation_id, classes, mode, per_wsi=False):
    if mode == "detection":
        bb = result
        return {
            "segmentation": [[
                bb["x"], bb["y"],
                bb["x"] + bb["w"], bb["y"],
                bb["x"] + bb["w"], bb["y"] + bb["h"],
                bb["x"], bb["y"] + bb["h"]
            ]],
            "area": bb["w"]*bb["h"],
            "iscrowd": 0,
            "image_id": image_id,
            "bbox": [bb["x"], bb["y"], bb["w"], bb["h"]],
            "category_id": classes.index(bb["class"]) + 1,
            "id": annotation_id
        }
    elif mode == "segmentation":
        mask = result
        mask_img = cv2.imread(mask["coords"], 0)
        contours, _ = cv2.findContours(
            mask_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        annotations = []
        for contour in contours:
            contour = contour.reshape(-1, 2)
            if per_wsi:
                contour += [offsetx, offsety]
            minx, miny = list(map(int, contour.min(axis=0)))
            maxx, maxy = list(map(int, contour.max(axis=0)))
            annotations.append({
                "segmentation": contour.ravel().tolist(),
                "area": int((mask_img == 1).sum()),
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [minx, miny, maxx - minx, maxy - miny],
                "category_id": classes.index(mask["class"]) + 1,
                "id": annotation_id
            })
        return annotations


if __name__ == '__main__':
    converter = ToCOCOConverter()
    converter.convert()
