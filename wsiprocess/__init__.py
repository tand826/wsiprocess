from .slide import Slide
from .patcher import Patcher
from .annotation import Annotation
from .rule import Rule


def slide(path):
    return Slide(path)


def annotation(path):
    return Annotation(path)


def rule(path):
    return Rule(path)


def patcher(slide, method, annotation=False, save_to=".", patch_width=256,
            patch_height=256, overlap_width=1, overlap_height=1,
            on_foreground=0.8, on_annotation=1., start_sample=True,
            finished_sample=True, extract_patches=True):
    return Patcher(slide, method, annotation, save_to, patch_width,
                   patch_height, overlap_width, overlap_height, on_foreground,
                   on_annotation, start_sample, finished_sample,
                   extract_patches)
