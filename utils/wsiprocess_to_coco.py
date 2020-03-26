import sys
import argparse
import random
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import json


def main():
    args = getargs()
    make_dirs(args.save_to)
    ratio = get_ratio(args.ratio)
    train_paths, val_paths = make_link_to_images(args.root, args.save_to, ratio)
    train2014, val2014 = get_save_as(args.save_to)
    annotation = annotations_to_json(args.root)
    train2014, val2014 = make_output(args.save_to, annotation, train_paths, val_paths, train2014, val2014)
    save_data(args.save_to, train2014, val2014)


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("root",
                        type=Path,
                        help="Parent of results.json located")
    parser.add_argument("save_to", type=Path)
    parser.add_argument("ratio", help="Ratio of train and val. ie. 8:2")
    return parser.parse_args()


def make_dirs(save_to):
    if not save_to.exists():
        save_to.mkdir(parents=True)

    if not (save_to/"annotations").exists():
        (save_to/"annotations").mkdir()

    if not (save_to/"train2014").exists():
        (save_to/"train2014").mkdir()

    if not (save_to/"val2014").exists():
        (save_to/"val2014").mkdir()


def get_ratio(ratio):
    train, val = map(int, ratio.split(":"))
    print({"train": train/(train+val), "val": val/(train+val)})
    return {"train": train/(train+val), "val": val/(train+val)}


def make_link_to_images(root, save_to, ratio):
    classes = [i.stem for i in (root/"patches").glob("*")]
    for cls in classes:
        image_paths = list((root/"patches").glob("{}/*".format(cls)))
        random.shuffle(image_paths)

        train_paths = image_paths[:int(len(image_paths)*ratio["train"])]
        val_paths = image_paths[int(len(image_paths)*ratio["train"]):]

        with tqdm(train_paths, desc="Train imgs [{}]".format(cls)) as t:
            for image_path in t:
                if not (save_to/"train2014"/image_path.name).exists():
                    (save_to/"train2014"/image_path.name).symlink_to(image_path)

        with tqdm(val_paths, desc="Validation imgs [{}]".format(cls)) as t:
            for image_path in t:
                if not (save_to/"val2014"/image_path.name).exists():
                    (save_to/"val2014"/image_path.name).symlink_to(image_path)

    return train_paths, val_paths


def get_save_as(save_to):
    if not (save_to/"instances_train2014.json").exists():
        train2014 = {
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
        with open(save_to/"instances_train2014.json", "r") as f:
            train2014 = json.load(f)

    if not (save_to/"instances_val2014.json").exists():
        val2014 = {
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
        with open(save_to/"instances_val2014.json", "r") as f:
            val2014 = json.load(f)

    return train2014, val2014


def annotations_to_json(root):
    with open(root/"results.json", "r") as f:
        annotation = json.load(f)
    return annotation


def make_output(save_to, annotation, train_paths, val_paths, train2014, val2014):
    classes = annotation["classes"]
    slidestem = Path(annotation["slide"]).stem
    patch_width = annotation["patch_width"]
    patch_height = annotation["patch_height"]

    for idx, cls in enumerate(classes, 1):
        train2014["categories"].append({"supercategory": "", "id": idx, "name": cls})
        val2014["categories"].append({"supercategory": "", "id": idx, "name": cls})

    now = int(datetime.now().strftime('%Y%m%d%H%M%S'))
    with tqdm(train_paths, desc="Making annotation for train") as t:
        for idx, train_path in enumerate(t):
            image_id = now+idx
            x, y = map(int, train_path.stem.split("_")[-2:])
            train2014["images"].append(get_image_params(train_path, slidestem, x, y, patch_width, patch_height, image_id))
            train2014["annotations"].extend(get_annotation_params(annotation, classes, train_path, slidestem, x, y, patch_width, patch_width, image_id))

    now += len(train_paths)
    with tqdm(val_paths, desc="Making annotation for validation") as t:
        for idx, val_path in enumerate(t):
            image_id = now + idx
            x, y = map(int, val_path.stem.split("_")[-2:])
            val2014["images"].append(get_image_params(val_path, slidestem, x, y, patch_width, patch_height, image_id))
            val2014["annotations"].extend(get_annotation_params(annotation, classes, val_path, slidestem, x, y, patch_width, patch_width, image_id))

    return train2014, val2014


def get_image_params(file_name, slidestem, x, y, width, height, image_id):
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


def get_annotation_params(annotation, classes, file_name, slidestem, x, y, width, height, image_id):
    annotations = []
    for box in annotation["result"]:
        if box["x"] == x and box["y"] == y:
            if box.get("bbs"):
                for bb in box["bbs"]:
                    bb["x"] %= width
                    bb["y"] %= height
                    data = {
                        "segmentation": [],
                        "area": 0,
                        "iscrowd": 0,
                        "image_id": image_id,
                        "bbox": [bb["x"], bb["y"], bb["w"], bb["h"]],
                        "category_id": classes.index(bb["class"]) + 1,
                        "id": "{}_{}_{}".format(slidestem, x, y)
                    }
                    annotations.append(data)
            else:
                print("COCO dataset does not support classification annotations.")
                sys.exit()
    return annotations


def save_data(save_to, train2014, val2014):
    with open(save_to/"annotations"/"instances_train2014.json", "w") as f:
        json.dump(train2014, f, indent=4)

    with open(save_to/"annotations"/"instances_val2014.json", "w") as f:
        json.dump(val2014, f, indent=4)


if __name__ == '__main__':
    main()
