import unittest
import wsiprocess as wp
from slide import Slide
from annotation import Annotation
from inclusion import Inclusion
import os
from pathlib import Path


class WsiProcessTest(unittest.TestCase):

    def __init__(self):
        self.wsi = ["{}/datasets/CMU-1.ndpi".format(os.environ["HOME"])]
        self.method = ["none", "classification", "detection", "segmentation"]
        self.annotation = [Path()]

    def setUp(self):
        self.slide = Slide(self.wsi)
        self.wsi_width, self.wsi_height = self.slide.slide.dimensions

    def tearDown(self):
        pass

    def test_none(self):
        if self.annotation:
            annot = Annotation(self.annotation)

            if self.inclusion_relationship:
                inclusion = Inclusion(self.inclusion_relationship)
                annot.to_mask(wsi_height, wsi_width, inclusion)
            else:
                annot.to_mask(wsi_height, wsi_width)
            slide.to_patch(self.method, self.patch_width, self.overlap_width,
                           annot, self.patch_without_annotation,
                           self.only_foreground, self.patch_on_annotated,
                           self.start_sample, self.finished_sample,
                           self.extract_patches, self.magnification)

        else:
            slide.to_patch(self.method, self.patch_width, self.overlap_width,
                           self.only_foreground,
                           self.start_sample, self.finished_sample,
                           self.extract_patches, self.magnification)
