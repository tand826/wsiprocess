import argparse
from pathlib import Path
import wsiprocess as wp


class Args:
    def __init__(self):
        self.get_args()

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "wsi", type=str,
            help="Path to the target wsi.")
        parser.add_argument(
            "method", type=str,
            choices={"none", "classification", "detection", "segmentation"},
            help="Method to use.")
        parser.add_argument(
            "-st", "--save_to", type=Path, default=".",
            help="Where to save the data.")
        parser.add_argument(
            "-an", "--annotation", type=str, default=False,
            help="Path to the annotation xml file.")
        parser.add_argument(
            "-of", "--on_foreground", type=float, default=1.,
            help="The ratio of overlapped area of a patch and the foreground.")
        parser.add_argument(
            "-oa", "--on_annotation", type=float, default=1.,
            help="The ratio of overlapped area of a patch and the annotated.")
        parser.add_argument(
            "-pw", "--patch_width", type=int, default=256,
            help="Width of patches.")
        parser.add_argument(
            "-ph", "--patch_height", type=int, default=256,
            help="Height of patches.")
        parser.add_argument(
            "-ow", "--overlap_width", type=int, default=1,
            help="Width of the overlapped area of patches.")
        parser.add_argument(
            "-oh", "--overlap_height", type=int, default=1,
            help="Height of the overlapped area of patches")
        parser.add_argument(
            "-ss", "--start_sample", action="store_true",
            help="Generate samples at the start of the process.")
        parser.add_argument(
            "-fs", "--finished_sample", action="store_true",
            help="Generate samples at the end of the process.")
        parser.add_argument(
            "-ep", "--extract_patches", action="store_true",
            help="Extract the patches and save them as images.")
        parser.add_argument(
            "-ma", "--magnification", choices={40, 20, 10}, default=40,
            type=int,
            help="Magnification to process.")
        parser.add_argument(
            "-ru", "--rule", type=Path,
            help="File to define the inclusion / exclusion relationship.")

        args = parser.parse_args()
        for arg in vars(args):
            setattr(self, arg, getattr(args, arg))


def main():
    args = Args()
    slide = wp.slide(args.wsi)
    if args.rule:
        rule = wp.rule(args.rule)
    else:
        rule = False
    if args.annotation:
        annotation = wp.annotation(args.annotation)
        annotation.make_masks(slide, rule, foreground=True)
        annotation.classes.remove("foreground")
    else:
        annotation = wp.annotation("")
        if args.on_annotation:
            annotation.make_masks(slide, foreground=True)
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
        start_sample=args.start_sample,
        finished_sample=args.finished_sample,
        extract_patches=args.extract_patches)
    patcher.get_patch_parallel(annotation.classes)
