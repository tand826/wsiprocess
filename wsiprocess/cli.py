import argparse
import os
from pathlib import Path
import json
import wsiprocess as wp


class Args:
    def __init__(self, command):
        self.build_args(command)
        self.fillattrs(keys=[
            "annotation", "rule", "export_thumbs", "on_annotation", "minmax",
            "crop_bbox", "extract_foreground"])

    def set_base_parser(self):
        self.base_parser = argparse.ArgumentParser(
            description="wsiprocess command line tool")

    def set_common_args(self, parser):
        """ Common Arguments """
        parser.add_argument(
            "-st", "--save_to", type=Path, default=".",
            help="Where to save the data.")
        parser.add_argument(
            "-pw", "--patch_width", type=int, default=256,
            help="Width of patches.")
        parser.add_argument(
            "-ph", "--patch_height", type=int, default=256,
            help="Height of patches.")
        parser.add_argument(
            "-ow", "--overlap_width", type=int, default=0,
            help="Width of the overlapped area of patches.")
        parser.add_argument(
            "-oh", "--overlap_height", type=int, default=0,
            help="Height of the overlapped area of patches")
        parser.add_argument(
            "-ox", "--offset_x", type=int, default=0,
            help="The offset pixel along the x-axis.")
        parser.add_argument(
            "-oy", "--offset_y", type=int, default=0,
            help="The offset pixel along the y-axis.")
        parser.add_argument(
            "-dw", "--dot_bbox_width", type=int, default=30,
            help="Width of bbox translated from dot annotation.")
        parser.add_argument(
            "-dh", "--dot_bbox_height", type=int,
            help="Height of bbox translated from dot annotation.")
        parser.add_argument(
            "-ex", "--ext", type=str, default="png",
            help="Extension of extracted patches")
        parser.add_argument(
            "-ma", "--magnification", type=int,
            help="Magnification of extracted patches")
        parser.add_argument(
            "-mw", "--max_workers", type=int, default=os.cpu_count()//2,
            help="The maximum number of workers to use in patching.")
        parser.add_argument(
            "-ss", "--start_sample", action="store_true",
            help="Generate samples at the start of the process.")
        parser.add_argument(
            "-fs", "--finished_sample", action="store_true",
            help="Generate samples at the end of the process.")
        parser.add_argument(
            "-np", "--no_patches", action="store_true",
            help="Patcher run without extracting patches.")
        parser.add_argument(
            "-ep", "--extract_patches", action="store_true",
            help="[Not Available]Extract the patches and save them as images.")
        parser.add_argument(
            "-ve", "--verbose", action="store_true",
            help="Show progress bar while patching.")
        parser.add_argument(
            "-dr", "--dryrun", action="store_true",
            help="Run patching only for first 100 patches.")

    def set_wsi_arg(self, parser):
        parser.add_argument(
            "wsi", type=str,
            help="Path to the target wsi.")
        parser.add_argument(
            "-ba", "--backend", type=str,
            default="openslide",
            choices=["openslide", "pyvips", "bioformats"],
            help="Backend to use for reading the wsi.")

    def add_annotation_args(self, parser, slide_is_sparse=False):
        parser.add_argument(
            "annotation", type=str, default=False,
            help="Path to the annotation file.")
        parser.add_argument(
            "-ru", "--rule", type=Path,
            help="File to define the inclusion / exclusion relationship.")
        parser.add_argument(
            "-ef", "--extract_foreground", action="store_true",
            help="If set, wp extracts patches from foreground.")
        self.add_binarization_method(parser)
        self.add_on_foreground(parser, slide_is_sparse)
        self.add_on_annotation(parser, slide_is_sparse)

    def add_on_foreground(self, parser, slide_is_sparse=False):
        on_foreground_param = 0.0001 if slide_is_sparse else 0.01
        parser.add_argument(
            "-of", "--on_foreground", type=float, default=on_foreground_param,
            help="The ratio of overlapped area of a patch and the foreground.")

    def add_on_annotation(self, parser, slide_is_sparse=False):
        on_annotation_param = 0.0001 if slide_is_sparse else 0.01
        parser.add_argument(
            "-oa", "--on_annotation", type=json.loads, default=on_annotation_param,
            help="The ratio of overlapped area of a patch and the annotated.")

    def add_binarization_method(self, parser):
        parser.add_argument(
            "-mm", "--minmax", type=str, default=False,
            help="Get foreground mask as pixels from min to max. ie. 30-190")
        parser.add_argument(
            "-et", "--export_thumbs", action="store_true",
            help="Export thumbnails of masks.")

    def set_method_args(self):
        self.method_args = self.base_parser.add_subparsers(
            dest="method",
            help="Method to use.")
        self.method_args.required = True

    def set_evaluation_args(self):
        parser_eval = self.method_args.add_parser(
            "evaluation",
            help="Arguments for methods with no annotation data.")
        self.set_wsi_arg(parser_eval)
        self.add_on_foreground(parser_eval)
        self.add_binarization_method(parser_eval)
        self.set_common_args(parser_eval)

    def set_classification_args(self):
        """ Arguments for classification """
        parser_cls = self.method_args.add_parser(
            "classification",
            help="Arguments for classification tasks.")
        self.set_wsi_arg(parser_cls)
        self.add_annotation_args(parser_cls)
        self.set_common_args(parser_cls)

    def set_detection_args(self):
        """ Arguments for detection tasks. """
        parser_det = self.method_args.add_parser(
            "detection",
            help="Arguments for detection tasks.")
        self.set_wsi_arg(parser_det)

        parser_det.add_argument(
            "-vo", "--voc_style", action="store_true",
            help="Output as VOC style.")
        parser_det.add_argument(
            "-co", "--coco_style", action="store_true",
            help="Output as COCO style.")
        parser_det.add_argument(
            "-yo", "--yolo_style", action="store_true",
            help="Output as YOLO style.")
        parser_det.add_argument(
            "-ra", "--ratio", default="8:1:1",
            help="Ratio of the dataset size of train/validation/test phase.")
        parser_det.add_argument(
            "-cb", "--crop_bbox", default=False, action="store_true",
            help="Crop bounding boxes after patch extraction."
        )
        self.add_annotation_args(parser_det, slide_is_sparse=True)
        self.set_common_args(parser_det)

    def set_segmentation_args(self):
        """ Arguments for segmentation tasks. """
        parser_seg = self.method_args.add_parser(
            "segmentation",
            help="Arguments for segmentation tasksk."
        )
        self.set_wsi_arg(parser_seg)
        self.add_annotation_args(parser_seg)
        self.set_common_args(parser_seg)

    def build_args(self, command):
        """ Base Parser """
        self.set_base_parser()

        self.set_method_args()
        self.set_evaluation_args()
        self.set_classification_args()
        self.set_detection_args()
        self.set_segmentation_args()

        self.base_parser.parse_args(command, namespace=self)

    def fillattr(self, key: str):
        if not hasattr(self, key):
            setattr(self, key, False)

    def fillattrs(self, keys):
        for key in keys:
            self.fillattr(key)


def process_annotation(args, slide, rule):
    annotation = wp.annotation(args.annotation, slidename=slide.filename)
    annotation.dot_to_bbox(args.dot_bbox_width, args.dot_bbox_height)
    if args.minmax:
        min_, max_ = map(int, args.minmax.split("-"))
        annotation.make_masks(
            slide, rule, foreground_fn="minmax", min_=min_, max_=max_)
    else:
        annotation.make_masks(slide, rule, foreground_fn="otsu")

    return annotation


def main(command=None):
    args = Args(command)
    slide = wp.slide(args.wsi, backend=args.backend)
    rule = wp.rule(args.rule) if args.rule else False
    annotation = process_annotation(args, slide, rule)

    if args.export_thumbs:
        thumbs_dir = args.save_to/slide.filestem/"thumbs"
        thumbs_dir.mkdir(parents=True, exist_ok=True)
        annotation.export_thumb_masks(thumbs_dir)

    extract_classes = annotation.classes
    if not (args.extract_foreground and "foreground" in annotation.classes):
        extract_classes.remove("foreground")

    patcher = wp.patcher(
        slide, args.method,
        annotation=annotation,
        save_to=args.save_to,
        patch_width=args.patch_width,
        patch_height=args.patch_height,
        overlap_width=args.overlap_width,
        overlap_height=args.overlap_height,
        on_foreground=args.on_foreground,
        on_annotation=args.on_annotation,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        ext=args.ext,
        magnification=args.magnification,
        start_sample=args.start_sample,
        finished_sample=args.finished_sample,
        no_patches=args.no_patches,
        crop_bbox=args.crop_bbox,
        verbose=args.verbose,
        dryrun=args.dryrun)

    patcher.get_patch_parallel(
        extract_classes, max_workers=args.max_workers)

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
