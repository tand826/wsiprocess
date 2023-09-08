import json
from pathlib import Path

import torch
from torchvision import io

import wsiprocess as wp
from wsiprocess.cli import Args


class ClassificationDataset(torch.utils.data.Dataset):

    def __init__(self, dataset):
        self.dataset = dataset
        self.read_labels(self.dataset.coords)

    def read_labels(self, coords):
        normal_column = ["x", "y", "w", "h", "mask"]
        columns = list(set(coords.columns) - set(normal_column))
        self.labels = coords[columns]

    def __len__(self):
        return len(self.dataset.coords)

    def __getitem__(self, idx):
        coord = self.dataset.coords.iloc[idx]
        label = torch.tensor(self.labels.iloc[idx].tolist())
        return self.dataset.read_patch(**coord), label


class SegmentationDataset(torch.utils.data.Dataset):

    def __init__(self, dataset):
        if dataset.patch_config["no_patches"]:
            msg = "SegmentationDataset needs wsiprocess to have run without"
            msg += "no_patches because wsiprocess generates segmentation mask"
            msg += "from global view."
            raise NotImplementedError(msg)
        self.dataset = dataset
        self.path = Path(dataset.patch_config["save_to"]).parent
        self.read_masks(self.dataset.coords)

    def read_masks(self, coords):
        masks = coords.masks.str.replace("'", "\"")
        masks = masks.apply(lambda x: json.loads(x))

        self.masks = masks.apply(lambda x: x[0]["coords"])
        self.dataset.coords["label"] = masks.apply(lambda x: x[0]["class"])

    def __len__(self):
        return len(self.dataset.coords)

    def __getitem__(self, idx):
        coord = self.dataset.coords.iloc[idx]
        mask_path = str(self.path/self.masks.iloc[idx])
        mask = io.read_image(mask_path, mode=io.ImageReadMode.UNCHANGED)
        return self.dataset.read_patch(**coord), mask


def main(command, foreground_fn):
    args = Args(command)
    slide = wp.slide(args.wsi)
    rule = wp.rule(args.rule) if hasattr(args, "rule") and args.rule else False

    if args.method == "evaluation":
        annotation = wp.annotation()
    else:
        annotation = wp.annotation(args.annotation, slide=slide)
    annotation.dot_to_bbox(args.dot_bbox_width, args.dot_bbox_height)

    if foreground_fn:
        annotation.make_masks(slide, rule, foreground_fn=foreground_fn)
    elif hasattr(args, "minmax") and args.minmax:
        min_, max_ = map(int, args.minmax.split("-"))
        annotation.make_masks(
            slide, rule, foreground_fn="minmax", min_=min_, max_=max_)
    else:
        annotation.make_masks(slide, rule, foreground_fn="otsu")

    if hasattr(args, "extract_foreground"):
        if not (args.extract_foreground and "foreground" in annotation.classes):
            annotation.classes.remove("foreground")

    if hasattr(args, "export_thumbs") and args.export_thumbs:
        thumbs_dir = args.save_to/slide.filestem/"thumbs"
        if not thumbs_dir.exists():
            thumbs_dir.mkdir(parents=True)
        annotation.export_thumb_masks(thumbs_dir)

    if args.method == "evaluation":
        on_annotation = False
    else:
        on_annotation = args.on_annotation
    crop_bbox = args.crop_bbox if hasattr(args, "crop_bbox") else False

    patcher = wp.patcher(
        slide, args.method,
        annotation=annotation,
        save_to=args.save_to,
        patch_width=args.patch_width,
        patch_height=args.patch_height,
        overlap_width=args.overlap_width,
        overlap_height=args.overlap_height,
        on_foreground=args.on_foreground,
        on_annotation=on_annotation,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        ext=args.ext,
        magnification=args.magnification,
        start_sample=args.start_sample,
        finished_sample=args.finished_sample,
        no_patches=args.no_patches,
        crop_bbox=crop_bbox,
        verbose=args.verbose,
        dryrun=args.dryrun)
    patcher.get_patch_parallel(
        annotation.classes, max_workers=args.max_workers)

    if args.method == "detection":
        converter = wp.converter(
            args.save_to/slide.filestem,
            args.save_to/slide.filestem,
            args.ratio)
        if args.voc_style:
            converter.to_voc()
        if args.coco_style:
            converter.to_coco()
        if args.yolo_style:
            converter.to_yolo()

        if args.crop_bbox:
            patcher.get_mini_patch_parallel(annotation.classes)
