import wsiprocess as wp
import numpy as np


def example_function(thumb_gray):
    assert len(thumb_gray.shape) == 2
    assert isinstance(thumb_gray, np.ndarray)
    thresh = 100
    thumb_gray[thumb_gray > thresh] = 1
    thumb_gray[thumb_gray <= thresh] = 0
    assert np.sum((thumb_gray == 0) | (thumb_gray == 1)) == len(thumb_gray)
    return thumb_gray


slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("CMU-1_classification.xml")
annotation.make_masks(slide, foreground_fn=example_function)
patcher = wp.patcher(slide, "classification", annotation)
patcher.get_patch_parallel(["benign"])
