import argparse
import wsiprocess as wp


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("wsi")
    parser.add_argument("annotation")
    parser.add_argument("inclusion")
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
    args = args()
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
    print("detection")
    test_detection(args.wsi, args.annotation, args.inclusion)
    # print("segmentation")
    # test_segmentation(args.wsi, args.annotation, args.inclusion)
