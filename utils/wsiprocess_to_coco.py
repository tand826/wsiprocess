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
    print("")
    print("-----{}-----".format(args.root.name))
    ratio = get_ratio(args.ratio)
    train_paths, val_paths = make_link_to_images(
        args.root, args.save_to, ratio)
    train2014, val2014 = get_save_as(args.save_to)
    annotation = annotations_to_json(args.root)
    train2014, val2014 = make_output(
        args.save_to, annotation, train_paths, val_paths, train2014, val2014)
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
    return {"train": train/(train+val), "val": val/(train+val)}


def make_link_to_images(root, save_to, ratio):
    classes = [i.stem for i in (root/"patches").glob("*")]
    train_paths_allclasses = []
    val_paths_allclasses = []
    for cls in classes:
        image_paths = list((root/"patches").glob("{}/*".format(cls)))
        random.shuffle(image_paths)

        train_paths = image_paths[:int(len(image_paths)*ratio["train"])]
        val_paths = image_paths[int(len(image_paths)*ratio["train"]):]
        train_paths_allclasses += train_paths
        val_paths_allclasses += val_paths

        with tqdm(train_paths, desc="Train imgs [{}]".format(cls)) as t:
            for image_path in t:
                if not (save_to/"train2014"/image_path.name).exists():
                    (save_to/"train2014"/image_path.name).symlink_to(image_path)

        with tqdm(val_paths, desc="Validation imgs [{}]".format(cls)) as t:
            for image_path in t:
                if not (save_to/"val2014"/image_path.name).exists():
                    (save_to/"val2014"/image_path.name).symlink_to(image_path)

    return train_paths_allclasses, val_paths_allclasses


def get_save_as(save_to):
    if not (save_to/"annotations"/"instances_train2014.json").exists():
        train2014 = {
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
        with open(save_to/"annotations"/"instances_train2014.json", "r") as f:
            train2014 = json.load(f)

    if not (save_to/"annotations"/"instances_val2014.json").exists():
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
        with open(save_to/"annotations"/"instances_val2014.json", "r") as f:
            val2014 = json.load(f)

    return train2014, val2014


def annotations_to_json(root):
    with open(root/"results.json", "r") as f:
        annotation = json.load(f)
    annotation["classes"] = ["positive", "negative"]
    return annotation


def make_output(save_to, annotation, train_paths, val_paths, train2014, val2014):
    last_image_id, last_annotation_id = read_last_data(save_to)
    image_id = last_image_id + 1
    annotation_id = last_annotation_id + 1

    classes = annotation["classes"]
    slidestem = Path(annotation["slide"]).stem
    patch_width = annotation["patch_width"]
    patch_height = annotation["patch_height"]

    for cls in classes:
        train2014 = add_categories(train2014, cls)
        val2014 = add_categories(val2014, cls)

    with tqdm(train_paths, desc="Making annotation for train") as t:
        for idx, train_path in enumerate(t):
            x, y = map(int, train_path.stem.split("_")[-2:])
            image_params, image_id = get_image_params(
                train_path, slidestem, x, y, patch_width, patch_height, image_id)
            train2014["images"].append(image_params)

            annotation_params, annotation_id = get_annotation_params(
                annotation, classes, train_path, slidestem, x, y, patch_width, patch_width, image_id, annotation_id)
            train2014["annotations"].extend(annotation_params)

            image_id = image_id + 1

    with tqdm(val_paths, desc="Making annotation for validation") as t:
        for idx, val_path in enumerate(t):
            x, y = map(int, val_path.stem.split("_")[-2:])
            image_params, image_id = get_image_params(
                train_path, slidestem, x, y, patch_width, patch_height, image_id)
            val2014["images"].append(image_params)

            annotation_params, annotation_id = get_annotation_params(
                annotation, classes, train_path, slidestem, x, y, patch_width, patch_width, image_id, annotation_id)
            val2014["annotations"].extend(annotation_params)

            image_id = image_id + 1

    return train2014, val2014


def read_last_data(save_to):
    if (save_to/"annotations"/"instances_val2014.json").exists():
        with open(save_to/"annotations"/"instances_val2014.json", "r") as f:
            data = json.load(f)
            last_image_id = data["images"][-1]["id"]
            last_annotation_id = data["annotations"][-1]["id"]
    else:
        last_image_id, last_annotation_id = 0, 0

    return last_image_id, last_annotation_id


def add_categories(annotation, cls):
    categories = annotation["categories"]
    if cls == "half-positive":
        cls = "positive"
    classes = [cat["name"] for cat in categories]
    if cls not in classes:
        categories.append({
            "supercategory": "",
            "id": len(classes)+1,
            "name": cls}
        )
    return annotation


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
    }, image_id


def get_annotation_params(annotation, classes, file_name, slidestem, x, y, width, height, image_id, annotation_id):
    annotations = []
    for box in annotation["result"]:
        if box["x"] == x and box["y"] == y:
            if box.get("bbs"):
                for bb in box["bbs"]:
                    bb["x"] %= width
                    bb["y"] %= height
                    if bb["class"] == "half-positive":
                        bb["class"] = "positive"
                    data = {
                        "segmentation": [
                            bb["x"], bb["y"],
                            bb["x"] + bb["w"], bb["y"],
                            bb["x"] + bb["w"], bb["y"] + bb["h"],
                            bb["x"], bb["y"] + bb["h"]
                        ],
                        "area": -1,
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


def save_data(save_to, train2014, val2014):
    with open(save_to/"annotations"/"instances_train2014.json", "w") as f:
        json.dump(train2014, f, indent=4)

    with open(save_to/"annotations"/"instances_val2014.json", "w") as f:
        json.dump(val2014, f, indent=4)


if __name__ == '__main__':
    main()
