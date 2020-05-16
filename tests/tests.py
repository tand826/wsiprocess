import json
import pytest
import pyvips
import wsiprocess as wp

SAMPLEDIR = "../sample"
TESTDIR = "./"
WSIS = ("CMU-1.ndpi", "", "corrupted.ndpi")
METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
ANNOTATIONS = (
    "CMU-1_classification.xml",
    "CMU-1_detection.xml",
    "CMU-1_segmentation.xml",
    "test_emptyfile.txt")
SAVE_TOS = (".", "/", "")
ONFOREGROUNDS = (0, 1.0, 0.50000000001)
ONANNOTATIONS = (0, 1.0, 0.50000000001)
RULES = (
    "rule.json",
    "test_emptyfile.txt")
PATCH_SIZES = (256, 0, 1, 0.1, 1048576)
OVERLAP_SIZES = (1, 4096, 0, 0.1, 256)
OFFSET_X = (0, 1000, 1e10)
OFFSET_Y = (0, 1000, 1e10)
MAGNIFICATIONS = (10, 1, 80, 40, 20)
VOC_STYLE = (False, True)
COCO_STYLE = (False, True)
VOLO_STYLE = (False, True)


class Params:
    wsi = f"{SAMPLEDIR}/{WSIS[0]}"
    method = METHODS[0]
    annotation = f"{SAMPLEDIR}/{ANNOTATIONS[0]}"
    rule = f"{SAMPLEDIR}/{RULES[0]}"
    save_to = SAVE_TOS[0]
    on_annotation = ONANNOTATIONS[0]
    on_foreground = ONFOREGROUNDS[0]
    patch_width = PATCH_SIZES[0]
    patch_height = PATCH_SIZES[0]
    overlap_width = OVERLAP_SIZES[0]
    overlap_height = OVERLAP_SIZES[0]
    offset_x = OFFSET_X[0]
    offset_y = OFFSET_Y[0]
    magnification = MAGNIFICATIONS[0]
    extract_patches = True
    voc_style = VOC_STYLE[0]
    coco_style = COCO_STYLE[0]
    yolo_style = YOLO_STYLE[0]


def cli(params):
    slide = wp.slide(params.wsi)
    if params.rule:
        rule = wp.rule(params.rule)
    else:
        rule = False
    if params.annotation:
        annotation = wp.annotation(params.annotation)
        annotation.make_masks(slide, rule, foreground=True)
        annotation.classes.remove("foreground")
    else:
        annotation = wp.annotation("")
        if params.on_annotation:
            annotation.make_masks(slide, foreground=True)
    patcher = wp.patcher(
        slide, params.method,
        annotation=annotation,
        save_to=params.save_to,
        patch_width=params.patch_width,
        patch_height=params.patch_height,
        overlap_width=params.overlap_width,
        overlap_height=params.overlap_height,
        offset_x=params.offset_x,
        offset_y=params.offset_y,
        on_foreground=params.on_foreground,
        on_annotation=params.on_annotation,
        extract_patches=params.extract_patches)
    patcher.get_patch_parallel(annotation.classes)
    if params.voc_style or params.coco_style or params.yolo_style:
        converter = wp.converter(params.save_to/slide.filestem, params.save_to, params.ratio)
        if params.voc_style:
            converter.to_voc()
        if params.coco_style:
            converter.to_coco()
        if params.yolo_style:
            converter.to_yolo()


def test_cli_pass():
    # should go without any errors
    params = Params()
    cli(params)


def test_cli_wsi():
    # WSIS = ("CMU-1.ndpi", "", "corrupted.ndpi")
    params = Params()

    params.wsi = f"{SAMPLEDIR}/{WSIS[1]}"
    # with pytest.raises(pyvips.error.Error):
    #    cli(params)

    params.wsi = f"{TESTDIR}/{WSIS[2]}"
    with pytest.raises(pyvips.error.Error):
        cli(params)


def test_cli_method():
    # METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
    params = Params()

    params.method = METHODS[4]
    with pytest.raises(NotImplementedError):
        cli(params)


def test_cli_annotation():
    """
    ANNOTATIONS = (
        "CMU-1_classification.xml",
        "CMU-1_detection.xml",
        "CMU-1_segmentation.xml",
        "test_emptyfile.txt")
    """
    params = Params()

    params.annotation = f"{TESTDIR}/{ANNOTATIONS[3]}"
    cli(params)


def test_cli_method_annotation_combination():
    """
    METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
    ANNOTATIONS = (
        "CMU-1_classification.xml",
        "CMU-1_detection.xml",
        "CMU-1_segmentation.xml",
        "test_emptyfile.txt")
    """
    params = Params()

    # classification and segmentation can share annotation data
    params.method = METHODS[1]
    params.annotation = f"{SAMPLEDIR}/{ANNOTATIONS[2]}"
    cli(params)

    # detection can not share annotation data with other methods
    # TODO : how to detect annotation type?
    params.method = METHODS[2]
    params.annotation = f"{SAMPLEDIR}/{ANNOTATIONS[0]}"
    cli(params)

    params.method = METHODS[2]
    params.annotation = f"{SAMPLEDIR}/{ANNOTATIONS[2]}"
    cli(params)

    # segmentation can run with classification annotation
    params.method = METHODS[3]
    params.annotation = f"{SAMPLEDIR}/{ANNOTATIONS[0]}"
    cli(params)


def test_cli_rule():
    """
    RULES = (
        "rule.json",
        "test_emptyfile.txt")
    """
    params = Params()

    params.rule = RULES[1]
    with pytest.raises(json.decoder.JSONDecodeError):
        cli(params)


def test_cli_save_to():
    # SAVE_TOS = (".", "/", "")
    params = Params()

    params.save_to = SAVE_TOS[1]
    with pytest.raises(PermissionError):
        cli(params)

    params.save_to = SAVE_TOS[2]
    with pytest.raises(PermissionError):
        cli(params)


def test_cli_patch_overlap_size():
    # PATCH_SIZES = (256, 0, 1, 0.1, 1048576)
    # OVERLAP_SIZES = (1, 4096, 0, 0.1, 256)
    params = Params()

    # overlap_size > patch_size => error
    params.patch_height = params.patch_width = PATCH_SIZES[1]
    params.overlap_height = params.overlap_width = OVERLAP_SIZES[1]
    with pytest.raises(wp.error.SizeError):
        cli(params)

    # overlap_size = patch_size => error
    params = Params()
    params.overlap_height = params.overlap_width = OVERLAP_SIZES[4]
    with pytest.raises(wp.error.SizeError):
        cli(params)

    # patch_size > wsi_size => error
    params = Params()
    params.patch_height = params.patch_width = PATCH_SIZES[4]
    with pytest.raises(wp.error.SizeError):
        cli(params)

    # patch_size can not be zero
    params = Params()
    params.patch_height = params.patch_width = PATCH_SIZES[3]
    with pytest.raises(wp.error.SizeError):
        cli(params)

    # overlap_size can be zero
    params = Params()
    params.overlap_height = params.overlap_width = OVERLAP_SIZES[2]
    cli(params)

    # Add too PatchSizeTooSmallError


def test_offsets():
    # OFFSET_X = (0, 1000, 1e10)
    # OFFSET_Y = (0, 1000, 1e10)

    params = Params()
    params.offset_x = OFFSET_X[1]
    params.offset_y = OFFSET_Y[1]
    cli(params)

    # Runs with no patches because the offsets are too large.
    params.offset_x = OFFSET_X[2]
    params.offset_y = OFFSET_Y[2]
    cli(params)


def test_cli_on_annotation():
    # ONANNOTATIONS = (1.0, 0, 0.50000000001)
    params = Params()

    params.on_annotation = ONANNOTATIONS[1]
    cli(params)

    params.on_annotation = ONANNOTATIONS[2]
    cli(params)


def test_cli_on_foreground():
    # ONFOREGROUNDS = (1.0, 0, 0.50000000001)
    params = Params()

    params.on_foreground = ONFOREGROUNDS[1]
    cli(params)

    params.on_foreground = ONFOREGROUNDS[2]
    cli(params)


def test_cli_magnification():
    # MAGNIFICATIONS = (10, 1, 80, 40, 20)
    params = Params()

    """ Not activated yet
    params.magnification = MAGNIFICATIONS[1]
    with pytest.raises(ValueError):
        cli(params)

    params.magnification = MAGNIFICATIONS[2]
    with pytest.raises(ValueError):
        cli(params)

    params.magnification = MAGNIFICATIONS[3]
    with pytest.raises(ValueError):
        cli(params)

    params.magnification = MAGNIFICATIONS[4]
    with pytest.raises(ValueError):
        cli(params)
    """
