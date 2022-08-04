from pathlib import Path

import wsiprocess as wp
import cv2
import numpy as np

slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("CMU-1_classification.xml")
rule = wp.rule("rule.json")

# some functions to operate on the gray thumbnail


def otsu(x):
    mask = cv2.threshold(
        x, 0, 1, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    return mask


def dilate(x):
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.dilate(x, kernel=kernel, iterations=1)
    return mask


def erode(x):
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.erode(x, kernel=kernel, iterations=2)
    return mask


def foreground_fn(x):
    x = otsu(x)
    x = dilate(x)
    x = erode(x)
    return


# size = 5000 for more precise mask generation
annotation.make_masks(
    slide, rule, size=5000, foreground_fn=foreground_fn)

Path('CMU-1/thumbs').mkdir(exist_ok=True)
annotation.export_thumb_masks("CMU-1/thumbs")

patcher = wp.patcher(
    slide, "classification", annotation, on_annotation=0.1, on_foreground=0.1)
patcher.get_patch_parallel(["benign", "malignant"])
