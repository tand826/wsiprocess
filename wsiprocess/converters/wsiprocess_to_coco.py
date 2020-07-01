# -*- coding: utf-8 -*-
"""Converter to COCO style.

wsiprocess_to_coco is convert helper which convert the wsiprocess output for
COCO object detection format.
Only available for "detection" method, but works when extracting patches and
after extraction.

"""
import sys
import argparse
import shutil
import random
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


class ToCOCOConverter:
    """Converter class.
    """

    def __init__(self, params=False):
        if params:
            self.root = params["root"]
            self.save_to = params["save_to"]/"coco"
            self.ratio_arg = params["ratio_arg"]
        else:
            self.getargs()
        self.get_ratio()
        self.make_dirs()

    def convert(self):
        self.make_link_to_images()
        self.get_save_as()
        self.annotations_to_json()
        self.make_output()
        self.save_data()

    def getargs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("root",
                            type=Path,
                            help="Parent of results.json located")
        parser.add_argument("-s", "--save_to", default="./wp/coco", type=Path)
        parser.add_argument("-r", "--ratio", default="8:1:1", help="Ratio of train and val and test ie. 8:1:1")
        args = parser.parse_args()
        self.root = args.root
        self.save_to = args.save_to
        self.ratio_arg = args.ratio

    def make_dirs(self):
        if not self.save_to.exists():
            self.save_to.mkdir(parents=True)

        if not (self.save_to/"annotations").exists():
            (self.save_to/"annotations").mkdir()

        if not (self.save_to/"train2014").exists():
            (self.save_to/"train2014").mkdir()

        if not (self.save_to/"val2014").exists():
            (self.save_to/"val2014").mkdir()

        if self.test_is_available:
            if not (self.save_to/"test2014").exists():
                (self.save_to/"test2014").mkdir()

    def get_ratio(self):
        self.test_is_available = len(self.ratio_arg.split(":")) == 3
        if self.test_is_available:
            train, val, test = map(int, self.ratio_arg.split(":"))
            self.ratio = {"train": train/(train+val+test), "val": val/(train+val+test), "test": test/(train+val+test)}
        else:
            train, val = map(int, self.ratio_arg.split(":"))
            self.ratio = {"train": train/(train+val), "val": val/(train+val)}

    def make_link_to_images(self):
        classes = [i.stem for i in (self.root/"patches").glob("*")]
        self.train_paths = []
        self.val_paths = []
        if self.test_is_available:
            self.test_paths = []
        for cls in classes:
            image_paths = list((self.root/"patches").glob("{}/*".format(cls)))
            random.shuffle(image_paths)

            train_count = int(len(image_paths)*self.ratio["train"])
            self.train_paths += image_paths[:train_count]
            if self.test_is_available:
                val_count = int(len(image_paths)*self.ratio["val"])
                self.val_paths += image_paths[train_count:train_count+val_count]
                self.test_paths += image_paths[train_count+val_count:]
            else:
                self.val_paths += image_paths[train_count:]

            self._make_link_to_images_per_phase("train", cls)
            self._make_link_to_images_per_phase("val", cls)
            if self.test_is_available:
                self._make_link_to_images_per_phase("test", cls)

    def _make_link_to_images_per_phase(self, phase, cls):
        if phase == "train":
            paths = self.train_paths
        elif phase == "val":
            paths = self.val_paths
        elif phase == "test":
            paths = self.test_paths
        with tqdm(paths, desc="{} imgs [{}]".format(phase, cls)) as t:
            for image_path in t:
                if not (self.save_to/"{}2014".format(phase)/image_path.name).exists():
                    shutil.copy(image_path, self.save_to/"{}2014".format(phase))
                    # (self.save_to/"{}2014".format(phase)/image_path.name).symlink_to(image_path)

    def get_save_as(self):
        if not (self.save_to/"annotations"/"instances_train2014.json").exists():
            self.train2014 = {
                "info": {
                    "description": "wsiprocess",
                    "url": "",
                    "version": "1.0",
                    "year": 2014,
                    "contributor": "",
                    "date_created": datetime.now().strftime('%Y/%m/%d_%H:%M:%S')
                },
                "licenses": [],
                "categories": [],
                "images": [],
                "annotations": []
            }

        else:
            with open(self.save_to/"annotations"/"instances_train2014.json", "r") as f:
                self.train2014 = json.load(f)

        if not (self.save_to/"annotations"/"instances_val2014.json").exists():
            self.val2014 = {
                "info": {
                    "description": "wsiprocess",
                    "url": "",
                    "version": "1.0",
                    "year": "2014",
                    "contributor": "",
                    "date_created": datetime.now().strftime('%Y/%m/%d_%H:%M:%S')
                },
                "licenses": [],
                "categories": [],
                "images": [],
                "annotations": []
            }
        else:
            with open(self.save_to/"annotations"/"instances_val2014.json", "r") as f:
                self.val2014 = json.load(f)

        if not (self.save_to/"annotations"/"instances_test2014.json").exists():
            self.test2014 = {
                "info": {
                    "description": "wsiprocess",
                    "url": "",
                    "version": "1.0",
                    "year": "2014",
                    "contributor": "",
                    "date_created": datetime.now().strftime('%Y/%m/%d_%H:%M:%S')
                },
                "licenses": [],
                "categories": [],
                "images": [],
                "annotations": []
            }
        else:
            with open(self.save_to/"annotations"/"instances_test2014.json", "r") as f:
                self.test2014 = json.load(f)

    def annotations_to_json(self):
        with open(self.root/"results.json", "r") as f:
            self.annotation = json.load(f)

    def make_output(self):
        last_image_id, last_annotation_id = self.read_last_data()
        image_id = last_image_id + 1
        annotation_id = last_annotation_id + 1

        classes = self.annotation["classes"]
        slidestem = Path(self.annotation["slide"]).stem
        patch_width = self.annotation["patch_width"]
        patch_height = self.annotation["patch_height"]

        for cls in classes:
            self.train2014 = self.add_categories(self.train2014, cls)
            self.val2014 = self.add_categories(self.val2014, cls)
            if self.test_is_available:
                self.test2014 = self.add_categories(self.test2014, cls)

        with tqdm(self.train_paths, desc="Making annotation for train") as t:
            for idx, train_path in enumerate(t):
                x, y = map(int, train_path.stem.split("_")[-2:])
                image_params, image_id = self.get_image_params(
                    train_path, slidestem, x, y, patch_width, patch_height, image_id)
                self.train2014["images"].append(image_params)

                annotation_params, annotation_id = self.get_annotation_params(
                    self.annotation, classes, train_path, slidestem, x, y, patch_width, patch_width, image_id, annotation_id)
                self.train2014["annotations"].extend(annotation_params)

                image_id += 1

        with tqdm(self.val_paths, desc="Making annotation for validation") as t:
            for idx, val_path in enumerate(t):
                x, y = map(int, val_path.stem.split("_")[-2:])
                image_params, image_id = self.get_image_params(
                    val_path, slidestem, x, y, patch_width, patch_height, image_id)
                self.val2014["images"].append(image_params)

                annotation_params, annotation_id = self.get_annotation_params(
                    self.annotation, classes, val_path, slidestem, x, y, patch_width, patch_width, image_id, annotation_id)
                self.val2014["annotations"].extend(annotation_params)

                image_id += 1

        if self.test_is_available:
            with tqdm(self.test_paths, desc="Making annotation for test") as t:
                for idx, test_path in enumerate(t):
                    x, y = map(int, test_path.stem.split("_")[-2:])
                    image_params, image_id = self.get_image_params(
                        test_path, slidestem, x, y, patch_width, patch_height, image_id)
                    self.test2014["images"].append(image_params)

                    annotation_params, annotation_id = self.get_annotation_params(
                        self.annotation, classes, test_path, slidestem, x, y, patch_width, patch_width, image_id, annotation_id)
                    self.test2014["annotations"].extend(annotation_params)

                    image_id += 1

    def read_last_data(self):
        if self.test_is_available:
            target = "instances_val2014.json"
        else:
            target = "instances_test2014.json"
        if (self.save_to/"annotations"/target).exists():
            with open(self.save_to/"annotations"/target, "r") as f:
                data = json.load(f)
                last_image_id = data["images"][-1]["id"]
                last_annotation_id = data["annotations"][-1]["id"]
        else:
            last_image_id, last_annotation_id = 0, 0

        return last_image_id, last_annotation_id

    def add_categories(self, annotation, cls):
        categories = annotation["categories"]
        classes = [cat["name"] for cat in categories]
        if cls not in classes:
            categories.append({
                "supercategory": "",
                "id": len(classes)+1,
                "name": cls}
            )
        return annotation

    def get_image_params(self, file_name, slidestem, x, y, width, height, image_id):
        return {
            "license": "",
            "file_name": str(file_name),
            "coco_url": "",
            "width": width,
            "height": height,
            "date_captured": "",
            "flickr_url": "",
            "id": image_id
        }, image_id

    def get_annotation_params(self, annotation, classes, file_name, slidestem, x, y, width, height, image_id, annotation_id):
        annotations = []
        for box in annotation["result"]:
            if box["x"] == x and box["y"] == y:
                if box.get("bbs"):
                    for bb in box["bbs"]:
                        bb["x"] %= width
                        bb["y"] %= height
                        data = {
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
                        annotation_id += 1
                        annotations.append(data)
                else:
                    print("COCO dataset does not support classification annotations.")
                    sys.exit()
        return annotations, annotation_id

    def save_data(self):
        with open(self.save_to/"annotations"/"instances_train2014.json", "w") as f:
            json.dump(self.train2014, f, indent=4)

        with open(self.save_to/"annotations"/"instances_val2014.json", "w") as f:
            json.dump(self.val2014, f, indent=4)

        if self.test_is_available:
            with open(self.save_to/"annotations"/"instances_test2014.json", "w") as f:
                json.dump(self.test2014, f, indent=4)


if __name__ == '__main__':
    converter = ToCOCOConverter()
    converter.convert()
