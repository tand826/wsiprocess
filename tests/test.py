import unittest
from pathlib import Path
import pyvips
import argparse
import wsiprocess as wp


class WsiprocessTest(unittest.TestCase):

    def setUp(self):
        self.test_slide_folder = Path("./sample")
        self.slide_exts = ["svs", "tiff", "ndpi", "scn", "bif", "zvi"]
        self.annotation_exts = ["xml", "json"]
        self.annotation_file_folder = Path("./sample")
        self.inclusion_file = "./sample/inclusion.txt"

    def tearDown(self):
        pass

    def test_slide(self):
        slide_paths = []
        for ext in self.slide_exts:
            slide_paths += list(self.test_slide_folder.glob("*/" + ext))
        for slide_path in slide_paths:
            slide = wp.slide(str(slide_path))
            self.assertTrue(type(slide) == pyvips.vimage.Image)

    def test_slide_thumbnail(self):
        slide_paths = []
        for ext in self.slide_exts:
            paths = list(self.test_slide_folder.glob("*/" + ext))
            if len(paths) > 0:
                slide_paths += paths[0]
        for slide_path in slide_paths:
            slide = wp.slide(str(slide_path))
            self.assertTrue(type(slide.get_thumbnail()) == pyvips.vimage.Image)

    def test_annotation(self):
        annotation_paths = []
        for ext in self.annotation_exts:
            annotation_paths += list(self.annotation_file_folder.glob(ext))
        for annotation_file in annotation_paths:
            annotation = wp.annotation(annotation_file)
            self.assertTrue(
                len(annotation.classes) > 0,
                "{} has no classes".format(annotation_file))
            sample_class = annotation.classes[0]
            self.assertTrue(type(annotation.mask_coords[sample_class]) == list)
            self.assertTrue(type(annotation.mask_coords[sample_class][0]) == list)
            self.assertTrue(type(annotation.mask_coords[sample_class][0][0]) == list)
            self.assertTrue(type(annotation.mask_coords[sample_class][0][0][0]) == int)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("test_slide_folder")
    parser.add_argument("annotation_file_folder")
    parser.add_argument("-i", "--inclusion")
    return parser.parse_args()


def test_slide(wsi):
    slide = wp.Slide(wsi)
    print(slide.width)


def test_annotation(wsi, annotation):
    slide = wp.Slide(wsi)
    annotation = wp.Annotation(annotation)
    annotation.make_masks(slide, foreground=True)
    annotation.export_thumb_mask(cls="foreground", save_to=".")
    annotation.export_thumb_masks(".")


def test_inclusion(inclusion):
    inclusion = wp.Inclusion(inclusion)


def test_none(wsi, annotation, inclusion):
    """
    [Arguments for Patcher]
    slide, method, annotation=False, save_to=".", patch_width=256, patch_height=256,
    overlap_width=1, overlap_height=1, on_foreground=1., on_annotation=1.,
    start_sample=True, finished_sample=True, extract_patches=True
    """
    slide = wp.Slide(wsi)

    # no annotation file
    print("none without annotation")
    patcher = wp.Patcher(slide, "none", start_sample=False, finished_sample=False, on_foreground=False, on_annotation=False)
    #patcher.get_patch_parallel()

    # with annotation file
    print("none with annotation")
    annotation = wp.Annotation(annotation)
    annotation.make_masks(slide, foreground=True)
    annotation.export_thumb_masks()
    patcher = wp.Patcher(slide, "none", annotation, start_sample=False, finished_sample=False, on_foreground=1., on_annotation=1.)
    patcher.get_patch_parallel(annotation.classes[0])

    # with annotation file and inclusion file
    print("none with anntation and inclusion")
    inclusion = wp.Inclusion(inclusion)
    annotation.make_masks(slide, inclusion, foreground=True)
    patcher = wp.Patcher(slide, "none", annotation, start_sample=False, finished_sample=False, on_foreground=1., on_annotation=1.)
    patcher.get_patch_parallel(annotation.classes[0])


def test_classification(wsi, annotation, inclusion):
    slide = wp.Slide(wsi)

    # with annotation file
    print("classification with annotation")
    annotation = wp.Annotation(annotation)
    annotation.make_masks(slide, foreground=True)
    patcher = wp.Patcher(slide, "classification", annotation, start_sample=False, finished_sample=False, on_foreground=1., on_annotation=1.)
    patcher.get_patch_parallel(annotation.classes[0])

    # with annotation file and inclusion file
    print("classification with annotation and inclusion")
    inclusion = wp.Inclusion(inclusion)
    annotation.make_masks(slide, inclusion, foreground=True)
    patcher = wp.Patcher(slide, "classification", annotation, start_sample=False, finished_sample=False, on_foreground=1., on_annotation=1.)
    patcher.get_patch_parallel(annotation.classes[0])


def test_detection(wsi, annotation, inclusion):
    slide = wp.Slide(wsi)

    # with annotation file
    print("detection with annotation")
    annotation = wp.Annotation(annotation)
    annotation.make_masks(slide, foreground=True)
    annotation.export_thumb_masks()
    patcher = wp.Patcher(slide, "detection", annotation, start_sample=False, finished_sample=False, on_foreground=0.5, on_annotation=0.01)
    patcher.get_patch_parallel("malignant")
    patcher.get_patch_parallel("benign")

    # with annotation file and inclusion file
    print("detection with annotation and inclusion")
    #inclusion = wp.Inclusion(inclusion)
    #annotation.make_masks(slide, inclusion, foreground=True)
    #patcher = wp.Patcher(slide, "detection", annotation, start_sample=False, finished_sample=False, on_foreground=0.5, on_annotation=0.01)
    #patcher.get_patch_parallel(annotation.classes[0])


def test_segmentation(wsi, annotation, inclusion):
    slide = wp.Slide(wsi)

    # with annotation file
    print("segmentation with annotation")
    annotation = wp.Annotation(annotation)
    annotation.make_masks(slide, foreground=True)
    patcher = wp.Patcher(slide, "segmentation", annotation, start_sample=False, finished_sample=False, on_foreground=0.5, on_annotation=0.3)
    patcher.get_patch_parallel(annotation.classes[0])

    # with annotation file and inclusion file
    print("segmentation with annotation and inclusion")
    inclusion = wp.Inclusion(inclusion)
    annotation.make_masks(slide, inclusion)
    patcher = wp.Patcher(slide, "segmentation", annotation, start_sample=False, finished_sample=False, on_foreground=0.5, on_annotation=0.3)
    # patcher.get_patch_parallel(annotation.classes[0])


if __name__ == '__main__':
    #args = args()
    # print("slide")
    # test_slide(args.wsi)
    # print("annotation")
    # test_annotation(args.wsi, args.annotation)
    # print("inclusion")
    # test_inclusion(args.inclusion)
    # print("none")
    # test_none(args.wsi, args.annotation, args.inclusion)
    # print("classification")
    # test_classification(args.wsi, args.annotation, args.inclusion)
    #print("detection")
    #test_detection(args.wsi, args.annotation, args.inclusion)
    # print("segmentation")
    # test_segmentation(args.wsi, args.annotation, args.inclusion)

    unittest.main()