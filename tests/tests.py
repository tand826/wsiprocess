import json
from pathlib import Path
import pytest
import pyvips
import openslide
import wsiprocess as wp
import wsiprocess.cli as cli

SAMPLEDIR = "../sample"
TESTDIR = "./"

METHODS = ("evaluation", "classification", "detection", "segmentation", "foo")
WSIS = (
    f"{TESTDIR}/test.tiff",
    None,
    f"{TESTDIR}/corrupted.ndpi")
ANNOTATIONS = (
    f"{SAMPLEDIR}/CMU-1_classification.xml",
    f"{SAMPLEDIR}/CMU-1_detection.xml",
    f"{SAMPLEDIR}/CMU-1_segmentation.xml",
    f"{TESTDIR}/test_emptyfile.txt")
RULES = (
    f"{SAMPLEDIR}/rule.json",
    f"{TESTDIR}/test_emptyfile.txt")
SAVE_TOS = (".", "/", "")
ONFOREGROUNDS = ("1.0", "0", "0.50000000001")
ONANNOTATIONS = ("1.0", "0", "0.50000000001")
MINMAXS = ("0-255", "100-200", "100-99")
PATCH_SIZES = ("256", "0", "1", "0.1", "1048576")
OVERLAP_SIZES = ("1", "4096", "0", "0.1", "256")
OFFSET_X = ("0", "1000", "1048576")
OFFSET_Y = ("0", "1000", "1048576")
DOT_BBOX_WIDTH = ("10", "0", "1000")
DOT_BBOX_HEIGHT = ("10", "0", "1000")
MAGNIFICATIONS = ("10", "1", "80", "40", "20")
VOC_STYLE = ("False", "True")
COCO_STYLE = ("False", "True")
YOLO_STYLE = ("False", "True")
VERBOSE = ("False", "True")


def test_make_small_pyramidal_tiff():
    assert Path(f"{SAMPLEDIR}/CMU-1.ndpi").exists(), "download CMU-1.ndpi"
    if not Path(f"{TESTDIR}/test.tiff").exists():
        slide = pyvips.Image.new_from_file(f"{SAMPLEDIR}/CMU-1.ndpi")
        slide_small = slide.crop(7000, 18000, 1280, 1280)
        slide_small.tiffsave(
            f"{TESTDIR}/test.tiff", compression="jpeg", pyramid=True,
            tile=True)


def test_cli_pass():
    # should go without any errors
    cli.main([
        METHODS[0], WSIS[0],
        "-of", ONFOREGROUNDS[0],
        "-st", SAVE_TOS[0],
        "-pw", PATCH_SIZES[0],
        "-ph", PATCH_SIZES[0],
        "-ow", OVERLAP_SIZES[0],
        "-oh", OVERLAP_SIZES[0],
        "-ox", OFFSET_X[0],
        "-oy", OFFSET_Y[0],
        "-dw", DOT_BBOX_WIDTH[0],
        "-dh", DOT_BBOX_HEIGHT[0]
    ])


def test_cli_wsi_blank():
    wsi = WSIS[1]
    with pytest.raises(wp.error.SlideLoadError):
        cli.main([METHODS[0], wsi])


def test_cli_wsi_corrupted():
    wsi = WSIS[2]
    with pytest.raises(openslide.lowlevel.OpenSlideUnsupportedFormatError):
        cli.main([METHODS[0], wsi])


def test_cli_method_none():
    method = METHODS[0]
    cli.main([method, WSIS[0]])


def test_cli_method_classification():
    method = METHODS[1]
    annotation = ANNOTATIONS[0]
    cli.main([method, WSIS[0], annotation])


def test_cli_method_detection():
    method = METHODS[1]
    annotation = ANNOTATIONS[1]
    cli.main([method, WSIS[0], annotation])


def test_cli_method_segmentation():
    method = METHODS[2]
    annotation = ANNOTATIONS[2]
    cli.main([method, WSIS[0], annotation])


def test_cli_method_notimplemented():
    # METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
    method = METHODS[3]
    # argparse does not catch invalid choice as Errors.
    cli.main([method, WSIS[0], ANNOTATIONS[0]])


def test_cli_annotation_emptyfile():
    """
    ANNOTATIONS = (
        "CMU-1_classification.xml",
        "CMU-1_detection.xml",
        "CMU-1_segmentation.xml",
        "test_emptyfile.txt")
    """
    method = METHODS[1]
    annotation = ANNOTATIONS[3]
    cli.main([method, WSIS[0], annotation])


def test_cli_none_with_annotation():
    method = METHODS[0]
    annotation = ANNOTATIONS[0]
    with pytest.raises(SystemExit):
        cli.main([method, WSIS[0], annotation])


def test_cli_classification_without_annotation():
    method = METHODS[1]
    with pytest.raises(SystemExit):
        cli.main([method, WSIS[0]])


def test_cli_detection_without_annotation():
    method = METHODS[2]
    with pytest.raises(SystemExit):
        cli.main([method, WSIS[0]])


def test_cli_segmentation_without_annotation():
    method = METHODS[3]
    with pytest.raises(SystemExit):
        cli.main([method, WSIS[0]])


def test_cli_rule_empty():
    # RULES = ("rule.json", "test_emptyfile.txt")
    rule = RULES[1]
    with pytest.raises(json.decoder.JSONDecodeError):
        cli.main([
            METHODS[1], WSIS[0], ANNOTATIONS[0],
            "-ru", rule
        ])


def test_cli_save_to_root():
    # SAVE_TOS = (".", "/", "")
    save_to = SAVE_TOS[1]
    with pytest.raises(OSError):
        cli.main([
            METHODS[0], WSIS[0],
            "-st", save_to
        ])


def test_cli_patch_too_small():
    # PATCH_SIZES = (256, 0, 1, 0.1, 1048576)
    patch_height = patch_width = PATCH_SIZES[1]
    with pytest.raises(wp.error.SizeError):
        cli.main([
            METHODS[0], WSIS[0],
            "-pw", patch_width,
            "-ph", patch_height
        ])


def test_cli_patch_too_large():
    patch_height = patch_width = PATCH_SIZES[4]
    with pytest.raises(wp.error.SizeError):
        cli.main([
            METHODS[0], WSIS[0],
            "-pw", patch_width,
            "-ph", patch_height
        ])


def test_cli_overlap_too_large():
    patch_height = patch_width = PATCH_SIZES[0]
    overlap_height = overlap_width = OVERLAP_SIZES[4]
    with pytest.raises(wp.error.SizeError):
        cli.main([
            METHODS[0], WSIS[0],
            "-pw", patch_width,
            "-ph", patch_height,
            "-ow", overlap_width,
            "-oh", overlap_height
        ])


def test_cli_offset_too_large():
    offset_x = OFFSET_X[2]
    offset_y = OFFSET_Y[2]
    with pytest.raises(wp.error.SizeError):
        cli.main([
            METHODS[0], WSIS[0],
            "-ox", offset_x,
            "-oy", offset_y
        ])


def test_cli_on_annotation_too_small():
    on_annotation = ONANNOTATIONS[1]
    with pytest.raises(wp.error.OnParamError):
        cli.main([
            METHODS[1], WSIS[0], ANNOTATIONS[0],
            "-oa", on_annotation
        ])


def test_cli_on_foreground():
    # ONFOREGROUNDS = (1.0, 0, 0.50000000001)
    on_foreground = ONFOREGROUNDS[1]
    with pytest.raises(wp.error.OnParamError):
        cli.main([
            METHODS[0], WSIS[0],
            "-of", on_foreground
        ])


def test_cli_dot_to_bbox():
    # DOT_BBOX_WIDTH = (10, 0, 1000)
    dot_bbox_width = DOT_BBOX_WIDTH[1]
    with pytest.raises(wp.error.SizeError):
        cli.main([
            METHODS[2], WSIS[0], ANNOTATIONS[1],
            "-dw", dot_bbox_width
        ])


def test_verbose():
    cli.main([METHODS[0], WSIS[0], "-ve"])
    cli.main([METHODS[1], WSIS[0], ANNOTATIONS[0], "-ve"])

    cli.main([METHODS[0], WSIS[0]])
    cli.main([METHODS[1], WSIS[0], ANNOTATIONS[0]])
