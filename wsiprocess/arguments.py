import argparse
from pathlib import Path


class Args:
    def __init__(self):
        self.get_args()

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("wsi", type=Path,
                            help="Path to the target wsi.")
        parser.add_argument("method", type=str,
                            choices={"none", "classification", "detection", "segmentation"},
                            help="Method to use.")
        parser.add_argument("-os", "--one_shot", action="store_true",
                            help="[For object_detection] One annotation extracted only once.")
        parser.add_argument("-wa", "--patch_without_annotation", action="store_true",
                            help="Extract patches without annotations")
        parser.add_argument("-od", "--output_dir", type=Path,
                            help="Where to save the data.")
        parser.add_argument("-an", "--annotation", type=Path,
                            help="Path to the annotation xml file.")
        parser.add_argument("-of", "--only_foreground", action="store_true",
                            help="Crop the patches only from the foreground.")
        parser.add_argument("-pa", "--patch_on_annotated", type=float, default=1.,
                            help="The ratio of overlapped area of a patch and the annotated area.")
        parser.add_argument("-pw", "--patch_width", type=int, default=254,
                            help="Width of patches.")
        parser.add_argument("-ph", "--patch_height", type=int, default=254,
                            help="Height of patches.")
        parser.add_argument("-ow", "--overlap_width", type=int, default=1,
                            help="Width of the overlapped area of patches.")
        parser.add_argument("-oh", "--overlap_height", type=int, default=1,
                            help="Height of the overlapped area of patches")
        parser.add_argument("-ss", "--start_sample", action="store_true",
                            help="Generate samples at the start of the process.")
        parser.add_argument("-fs", "--finished_sample", action="store_true",
                            help="Generate samples at the end of the process.")
        parser.add_argument("-ep", "--extract_patches", action="store_true",
                            help="Extract the patches and save them as images.")
        parser.add_argument("-ma", "--magnification", choices={40, 20, 10},
                            default=40, type=int,
                            help="Magnification to process.")
        parser.add_argument("-ie", "--inclusion_relationship", type=Path,
                            help="File to define the inclusion relationship.")

        args = parser.parse_args()
        for arg in vars(args):
            setattr(self, arg, getattr(args, arg))
