import argparse
from pathlib import Path
from lxml import etree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--classes", type=Path,
                        help="path to the classes.names")
    parser.add_argument("-r", "--root", type=Path,
                        help="Parent Directory which contains the xml files.")
    parser.add_argument("-s", "--save_to", type=Path)
    args = parser.parse_args()

    paths = get_paths(args.root)
    classes = get_classes(args.classes)
    for path in paths:
        annotations = to_yolo(path, classes)
        save_as_yolo(annotations, path, args.save_to)


def get_paths(root):
    return root.glob("*.xml")


def get_classes(path_classes):
    with open(path_classes, "r") as f:
        classes = [i.strip() for i in f.readlines()]
    return classes


def to_yolo(path, classes):

    tree = etree.parse(str(path))
    objects = tree.xpath("/annotation/object")
    annotations = []
    img_width = int(tree.xpath("/annotation/size/width")[0].text)
    img_height = int(tree.xpath("/annotation/size/height")[0].text)

    for obj in objects:
        try:
            label = classes.index(obj.xpath("name")[0].text)
        except ValueError:
            if obj.xpath("name")[0].text == "half-positive":
                label = classes.index("positive")
        xmin = int(obj.xpath("bndbox/xmin")[0].text)
        ymin = int(obj.xpath("bndbox/ymin")[0].text)
        xmax = int(obj.xpath("bndbox/xmax")[0].text)
        ymax = int(obj.xpath("bndbox/ymax")[0].text)

        xcenter = (xmin + xmax) / 2 / img_width
        ycenter = (ymin + ymax) / 2 / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height
        annotations.append(f"{label} {xcenter} {ycenter} {width} {height}")
    return annotations


def save_as_yolo(annotations, path, save_to):
    if len(annotations) == 0:
        return

    with open(save_to/f"{path.stem}.txt", "w") as f:
        f.write("\n".join(annotations))


if __name__ == '__main__':
    main()
