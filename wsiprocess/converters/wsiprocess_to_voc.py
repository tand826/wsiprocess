# -*- coding: utf-8 -*-
"""Converter to VOC style.

wsiprocess_to_voc is convert helper which convert the wsiprocess output for
VOC object detection format.
Only available for "detection" method, but works when extracting patches and
after extraction.

"""
import argparse
import random
from lxml import etree
from pathlib import Path
from PIL import Image
import json
import shutil


class ToVOCConverter:
    """Converter class."""

    def __init__(self, params=False):
        """

        Args:
            params(dict): Dict contains root, save_to, ratio_arg

        'root' should be like below

        ./root
        ├── patches
        │   └── class_a
        │       ├── 001.png
        │       ├── 002.png

        │       └── 100.png
        └── results.json
        """
        if params:
            self.root = params["root"]
            self.save_to = params["save_to"]/"voc"
            self.ratio = params["ratio_arg"]
        else:
            self.getargs()
        self.makedirs()

    def convert(self):
        self.read_result_file()
        self.make_tree()
        self.move_to_test()

    def getargs(self):
        parser = argparse.ArgumentParser(description="wsiprocess_to_voc")
        parser.add_argument("root", type=Path)
        parser.add_argument("-s", "--save_to", default="./wp/voc", type=Path)
        parser.add_argument("-r", "--ratio", default="8:1:1")
        args = parser.parse_args()
        self.root = args.root
        self.save_to = args.save_to
        self.ratio = args.ratio

    def makedirs(self):
        self.mkdirs("VOC2007")
        self.mkdirs("VOC2012")
        Path(f"{self.save_to}/VOC2012/ImageSets/Main/trainval.txt").touch()

    def mkdirs(self, subdirectory):
        parent_dir = self.save_to/subdirectory
        (parent_dir/"Annotations").mkdir(exist_ok=True, parents=True)
        (parent_dir/"JPEGImages").mkdir(exist_ok=True, parents=True)
        (parent_dir/"ImageSets/Main").mkdir(exist_ok=True, parents=True)

    def read_result_file(self):
        with open(self.root/"results.json", "r") as f:
            self.result_wp = json.load(f)

    def make_tree(self):
        self.results = []
        for result in self.result_wp["result"]:
            tree = VOCTree(self.root, self.save_to/"VOC2007", result, self.result_wp["patch_width"], self.result_wp["patch_height"])
            tree.to_xml()
            cls = result["bbs"][0]["class"]
            # for cls in classes:
            # to_jpg(f"{args.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg", args.save_to/"VOC2007"/"JPEGImages")
            src = f"{self.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg"
            dst = f"{self.save_to}/VOC2007/JPEGImages/{self.root.name}_{result['x']:06}_{result['y']:06}.jpg"
            shutil.copy(src, dst)
            self.results.append(f"{self.root.name}_{result['x']:06}_{result['y']:06}\n")

    def to_jpg(self, src, dst):
        img = Image.open(src).convert("RGB")
        imgname = f"{Path(src).parent.parent.parent.name}_{Path(src).stem}"
        img.save(f"{dst}/{imgname}.jpg", quality=95)

    def move_to_test(self):
        """
        If ratio has only two parameters like "8:2", trainval.txt and test.txt would be generated.
        If ratio has 3 params like "8:1:1", trainval.txt, val.txt and text.txt would be generated.
        """
        trainval_path = f"{self.save_to}/VOC2007/ImageSets/Main/trainval.txt"
        test_path = f"{self.save_to}/VOC2007/ImageSets/Main/test.txt"
        random.shuffle(self.results)

        test_is_available = len(self.ratio.split(":")) == 3
        if test_is_available:
            train, val, test = map(int, self.ratio.split(":"))
            ratio = {"train": train/(train+val+test), "val": val/(train+val+test), "test": test/(train+val+test)}
            train_count = int(len(self.results) * ratio["train"])
            val_count = int(len(self.results) * ratio["val"])
            val_path = f"{self.save_to}/VOC2007/ImageSets/Main/val.txt"

            with open(trainval_path, "a") as f:
                f.writelines(self.results[:train_count])
            with open(val_path, "a") as f:
                f.writelines(self.results[train_count:train_count+val_count])
            with open(test_path, "a") as f:
                f.writelines(self.results[train_count+val_count:])

        else:
            train, val = map(int, ratio.split(":"))
            ratio = {"train": train/(train+val), "val": val/(train+val)}
            train_count = int(len(self.results) * ratio["train"])

            with open(trainval_path, "a") as f:
                f.writelines(self.results[:train_count])
            with open(test_path, "a") as f:
                f.writelines(self.results[train_count:])


class VOCTree:

    def __init__(self, root, save_to, result, patch_width, patch_height):
        self.root = root
        self.save_to = save_to

        self.x = result["x"]
        self.y = result["y"]
        self.w = result["w"]
        self.h = result["h"]
        self.bbs = result["bbs"]
        self.patch_width = patch_width
        self.patch_height = patch_height
        self.imgname = f"{self.x:06}_{self.y:06}.png"
        self.out_name = f"{root.name}_{self.x:06}_{self.y:06}.xml"

        self.tree = etree.Element("annotation")
        self.main_branches = ["folder", "filename", "source", "owner", "size", "segmented"]
        self.sub_branches = {"source": ["database", "annotation", "image", "flickrid"],
                             "owner": ["flickrid", "name"],
                             "size": ["width", "height", "depth"]}

        self.make_template()
        self.set_size()
        self.add_objects()

    def make_template(self):
        self.add_main_branches()
        self.add_sub_branches()
        self.add_base_text()

    def add_main_branches(self):
        for branch in self.main_branches:
            etree.SubElement(self.tree, branch)

    def add_sub_branches(self):
        for main, sub_branches in self.sub_branches.items():
            main_branch = self.tree.find(main)
            for branch in sub_branches:
                etree.SubElement(main_branch, branch)

    def add_base_text(self):
        self.add_text("folder", "wsiprocess")
        self.add_text("filename", self.imgname)
        self.add_text("source/database", "original")
        self.add_text("/annotation/source/annotation", "PASCAL_style")

    def add_text(self, branch, text):
        target = self.tree.xpath(branch)[0]
        target.text = str(text)

    def set_size(self):
        # img_path = self.root/"patches"/"mitosis_figure"/self.imgname
        # img = Image.open(str(img_path))
        # w, h = img.size
        depth = 3  # len(img.getbands())
        self.add_text("/annotation/size/width", self.patch_width)
        self.add_text("/annotation/size/height", self.patch_height)
        self.add_text("/annotation/size/depth", depth)

    def add_objects(self):
        for bb in self.bbs:
            obj = etree.Element("object")
            name = etree.SubElement(obj, "name")
            name.text = bb["class"]
            etree.SubElement(obj, "pose")
            etree.SubElement(obj, "truncated")
            difficult = etree.SubElement(obj, "difficult")
            difficult.text = str(0)

            bndbox = etree.SubElement(obj, "bndbox")
            etree.SubElement(bndbox, "xmin")
            etree.SubElement(bndbox, "ymin")
            etree.SubElement(bndbox, "xmax")
            etree.SubElement(bndbox, "ymax")

            xmin = bb["x"]
            ymin = bb["y"]
            xmax = int(bb["x"] + int(bb["w"]))
            ymax = int(bb["y"] + int(bb["h"]))

            if xmin == xmax:
                if xmin == 0:
                    xmax += 1
                else:
                    xmin -= 1
            if ymin == ymax:
                if ymin == 0:
                    ymax += 1
                else:
                    ymin -= 1

            obj.xpath("/object/bndbox/xmin")[0].text = str(xmin)
            obj.xpath("/object/bndbox/ymin")[0].text = str(ymin)
            obj.xpath("/object/bndbox/xmax")[0].text = str(xmax)
            obj.xpath("/object/bndbox/ymax")[0].text = str(ymax)

            self.tree.insert(-1, obj)

    def to_xml(self):
        with open(f"{self.save_to}/Annotations/{self.out_name}", "wb") as f:
            out_tree = etree.ElementTree(self.tree)
            out_tree.write(f,
                           pretty_print=True,
                           xml_declaration=True,
                           encoding="UTF-8")


if __name__ == '__main__':
    converter = ToVOCConverter()
    converter.convert()
