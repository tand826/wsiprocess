# -*- coding: utf-8 -*-
"""Converter to YOLO style.

wsiprocess_to_yolo is convert helper which convert the wsiprocess output for
YOLO object detection format.
Only available for "detection" method, but works when extracting patches and
after extraction.

"""
import argparse
import random
from pathlib import Path
import json
import shutil

"""
'root' should be like below

./root
├── patches
│   └── class_a
│       ├── 001.png
│       ├── 002.png

│       └── 100.png
└── results.json
"""


class ToYOLOConverter:

    def __init__(self, params=False):
        if params:
            self.root = params["root"]
            self.save_to = params["save_to"]/"yolo"
            self.ratio_arg = params["ratio_arg"]
        else:
            self.getargs()
        self.parse_ratio()
        self.image_paths = {}
        self.read_result_file()
        self.makedirs()

    def convert(self):
        self.get_image_paths()
        self.make_images()
        self.make_labels()
        self.make_paths()

    def getargs(self):
        parser = argparse.ArgumentParser(description="wsiprocess_to_voc")
        parser.add_argument("root", type=Path)
        parser.add_argument("-s", "--save_to", default="./wp/yolo", type=Path)
        parser.add_argument("-r", "--ratio", default="8:1:1")
        args = parser.parse_args()
        self.root = args.root
        self.save_to = args.save_to
        self.ratio_arg = args.ratio

    def read_result_file(self):
        with open(self.root/"results.json", "r") as f:
            self.result_wp = json.load(f)
        self.classes = self.result_wp["classes"]
        self.filestem = Path(self.result_wp['slide']).stem
        self.image_paths = {cls: list() for cls in self.classes}

    def makedirs(self):
        if not self.save_to.exists():
            self.save_to.mkdir(parents=True)
        if not (self.save_to/"images").exists():
            (self.save_to/"images").mkdir(parents=True)
        if not (self.save_to/"labels").exists():
            (self.save_to/"labels").mkdir(parents=True)
        if not (self.save_to/"paths").exists():
            (self.save_to/"paths").mkdir(parents=True)

    def parse_ratio(self):
        self.test_is_available = len(self.ratio_arg.split(":")) == 3
        if self.test_is_available:
            train, val, test = map(int, self.ratio_arg.split(":"))
            self.ratio = {"train": train/(train+val+test), "val": val/(train+val+test), "test": test/(train+val+test)}
        else:
            train, val = map(int, self.ratio_arg.split(":"))
            self.ratio = {"train": train/(train+val), "val": val/(train+val)}

    def get_image_paths(self):
        for cls in self.classes:
            self.image_paths[cls] = [str(i.resolve()) for i in (self.root/"patches"/cls).glob("*.jpg")]
            random.shuffle(self.image_paths[cls])

    def make_images(self):
        for cls in self.classes:
            for path in self.image_paths[cls]:
                filename = f"{self.filestem}_{Path(path).name}"
                shutil.copy(path, self.save_to/"images"/filename)

    def make_labels(self):
        patch_width = self.result_wp["patch_width"]
        patch_height = self.result_wp["patch_height"]
        for patch in self.result_wp["result"]:
            bbs = []
            for bb in patch["bbs"]:
                label = self.classes.index(bb["class"])
                xcenter = (bb["x"] + bb["w"]/2) / patch_width
                ycenter = (bb["y"] + bb["h"]/2) / patch_height
                width = bb["w"] / patch_width
                height = bb["h"] / patch_height
                bbs.append(f"{label} {xcenter} {ycenter} {width} {height}\n")
            with open(self.save_to/"labels"/f"{self.filestem}_{patch['x']:06}_{patch['y']:06}.txt", "w") as f:
                f.writelines(bbs)
        with open(self.save_to/"yolo.names", "w") as f:
            f.write("\n".join(self.classes))

    def make_paths(self):
        """
        If ratio has only two parameters like "8:2", trainval.txt and test.txt would be generated.
        If ratio has 3 params like "8:1:1", trainval.txt, val.txt and text.txt would be generated.
        """
        train_path = f"{self.save_to}/paths/train.txt"
        test_path = f"{self.save_to}/paths/test.txt"
        if self.test_is_available:
            val_path = f"{self.save_to}/paths/val.txt"

        for cls in self.classes:
            if self.test_is_available:
                train_count = int(len(self.image_paths[cls]) * self.ratio["train"])
                val_count = int(len(self.image_paths[cls]) * self.ratio["val"])

                with open(train_path, "a") as f:
                    paths = self.image_paths[cls][:train_count]
                    renamed = [self.rename_path(path) for path in paths]
                    f.writelines(renamed)
                with open(val_path, "a") as f:
                    paths = self.image_paths[cls][train_count:train_count+val_count]
                    renamed = [self.rename_path(path) for path in paths]
                    f.writelines(renamed)
                with open(test_path, "a") as f:
                    paths = self.image_paths[cls][train_count+val_count:]
                    renamed = [self.rename_path(path) for path in paths]
                    f.writelines(renamed)

            else:
                train_count = int(len(self.image_paths[cls]) * self.ratio["train"])

                with open(train_path, "a") as f:
                    paths = self.image_paths[cls][:train_count]
                    renamed = [self.rename_path(path) for path in paths]
                    f.writelines(renamed)
                with open(test_path, "a") as f:
                    paths = self.image_paths[cls][train_count:]
                    renamed = [self.rename_path(path) for path in paths]
                    f.writelines(renamed)

    def rename_path(self, path):
        return str(self.save_to/"images"/f"{self.filestem}_{Path(path).name}\n")


if __name__ == '__main__':
    converter = ToYOLOConverter()
    converter.convert()
