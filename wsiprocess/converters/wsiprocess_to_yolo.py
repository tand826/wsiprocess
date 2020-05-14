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
            self.save_to = params["save_to"]
            self.ratio = params["ratio_arg"]
        else:
            self.getargs()
        self.makedirs()
        self.parse_ratio()
        self.image_paths = {}

    def convert(self):
        self.read_result_file()
        self.get_classes()
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

    def makedirs(self):
        if not self.save_to.exists():
            self.save_to.mkdir(parent=True)
        if not (self.save_to/"images").exists():
            (self.save_to/"images").mkdir(parent=True)
        if not (self.save_to/"labels").exists():
            (self.save_to/"labels").mkdir(parent=True)
        if not (self.save_to/"paths").exists():
            (self.save_to/"paths").mkdir(parent=True)

    def parse_ratio(self):
        self.test_is_available = len(self.ratio_arg.split(":")) == 3
        if self.test_is_available:
            train, val, test = map(int, self.ratio.split(":"))
            self.ratio = {"train": train/(train+val+test), "val": val/(train+val+test), "test": test/(train+val+test)}
        else:
            train, val = map(int, ratio.split(":"))
            self.ratio = {"train": train/(train+val), "val": val/(train+val)}

    def read_result_file(self):
        with open(self.root/"results.json", "r") as f:
            self.result_wp = json.load(f)

    def get_classes(self):
        self.classes = self.result_wp.classes

    def get_image_paths(self):
        for cls in self.classes:
            self.image_paths[cls] = [str(i.resolve()) for i in (self.root/"patches"/cls).glob("*.jpg")]
            random.shuffle(self.image_paths[cls])

    def make_images(self):
        for path in self.image_paths:
            shutil.copy(path, self.save_to/"images")

    def make_labels(self):
        """
        for result in self.result_wp["result"]:
            cls = result["bbs"][0]["class"]
            # for cls in classes:
            # to_jpg(f"{args.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg", args.save_to/"VOC2007"/"JPEGImages")
            src = f"{self.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg"
            dst = f"{self.save_to}/VOC2007/JPEGImages/{self.root.name}_{result['x']:06}_{result['y']:06}.jpg"
            shutil.copy(src, dst)
            self.results.append(f"{self.root.name}_{result['x']:06}_{result['y']:06}\n")
        """

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
                    f.writelines(self.image_paths[cls][:train_count])
                with open(val_path, "a") as f:
                    f.writelines(self.image_paths[cls][train_count:train_count+val_count])
                with open(test_path, "a") as f:
                    f.writelines(self.image_paths[cls][train_count+val_count:])

            else:
                train_count = int(len(self.image_paths[cls]) * self.ratio["train"])

                with open(train_path, "a") as f:
                    f.writelines(self.image_paths[cls][:train_count])
                with open(test_path, "a") as f:
                    f.writelines(self.image_paths[cls][train_count:])




if __name__ == '__main__':
    converter = ToYOLOConverter()
    converter.convert()
