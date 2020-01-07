import argparse
from lxml import etree
from pathlib import Path
from PIL import Image
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


def main():
    parser = argparse.ArgumentParser(description="wsiprocess_to_voc")
    parser.add_argument("root", type=Path)
    parser.add_argument("-st", "--save_to", default="./data", type=Path)
    args = parser.parse_args()

    mkdirs(args.save_to/"VOC2007")
    mkdirs(args.save_to/"VOC2012")
    Path(f"{args.save_to}/VOC2012/ImageSets/Main/trainval.txt").touch()

    results_json = read_json(args.root)
    classes = results_json["classes"]
    patch_width = results_json["patch_width"]
    patch_height = results_json["patch_height"]
    with open(f"{args.save_to}/VOC2007/ImageSets/Main/trainval.txt", "a")as f:
        for result in results_json["result"]:
            tree = Tree(args.root, args.save_to/"VOC2007", result, patch_width, patch_height)
            tree.to_xml()
            cls = result["bbs"][0]["class"]
            # for cls in classes:
            # to_jpg(f"{args.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg", args.save_to/"VOC2007"/"JPEGImages")
            src = f"{args.root}/patches/{cls}/{result['x']:06}_{result['y']:06}.jpg"
            dst = f"{args.save_to}/VOC2007/JPEGImages"
            shutil.copy(src, dst)
            f.write(f"{args.root.stem}_{result['x']:06}_{result['y']:06}\n")


def mkdirs(save_to):
    (save_to/"Annotations").mkdir(exist_ok=True, parents=True)
    (save_to/"JPEGImages").mkdir(exist_ok=True, parents=True)
    (save_to/"ImageSets/Main").mkdir(exist_ok=True, parents=True)


def read_json(root):
    with open(root/"results.json", "r") as f:
        result = json.load(f)
    return result


def to_jpg(src, dst):
    img = Image.open(src).convert("RGB")
    imgname = f"{Path(src).parent.parent.parent.stem}_{Path(src).stem}"
    img.save(f"{dst}/{imgname}.jpg", quality=95)


class Tree:

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
        self.out_name = f"{root.stem}_{self.x:06}_{self.y:06}.xml"

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
    main()
