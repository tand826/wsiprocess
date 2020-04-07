import pytest
import wsiprocess as wp

BASEDIR = "../sample"
WSIS = ("CMU-1.ndpi", "", "corrupted.ndpi")
METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
ANNOTATIONS = (
    "CMU-1_classification.xml",
    "CMU-1_detection.xml",
    "CMU-1_segmentation.xml",
    "test_emptyfile.txt")
SAVE_TOS = (".", "/", "")
ONFOREGROUNDS = (1.0, 0, 0.50000000001)
ONANNOTATIONS = (1.0, 0, 0.50000000001)
RULES = (
    "rule.json",
    "test_emptyfile.txt")
PATCH_SIZES = (256, 0, 1, 0.1, 4096)
OVERLAP_SIZES = (1, 4096, 0, 0.1, 256)
MAGNIFICATIONS = (10, 1, 80, 40, 20)


class Params:
    wsi = f"{BASEDIR}/{WSIS[0]}"
    method = METHODS[0]
    annotation = f"{BASEDIR}/{ANNOTATIONS[0]}"
    rule = f"{BASEDIR}/{RULES[0]}"
    save_to = SAVE_TOS[0]
    on_annotation = ONANNOTATIONS[0]
    on_foreground = ONFOREGROUNDS[0]
    patch_width = PATCH_SIZES[0]
    patch_height = PATCH_SIZES[0]
    overlap_width = OVERLAP_SIZES[0]
    overlap_height = OVERLAP_SIZES[0]
    magnification = MAGNIFICATIONS[0]
    extract_patches = True


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
        slide, method,
        annotation=annotation,
        save_to=params.save_to,
        patch_width=params.patch_width,
        patch_height=params.patch_height,
        overlap_width=params.overlap_width,
        overlap_height=params.overlap_height,
        on_foreground=params.on_foreground,
        on_annotation=params.on_annotation,
        extract_patches=params.extract_patches)
    patcher.get_patch_parallel(annotation.classes)


def test_cli_pass():
    # should go without any errors
    params = Params()
    try:
        cli(wsi, method, annotation, rule, save_to, on_annotation,
            on_foreground, patch_width, patch_height, overlap_width,
            overlap_height, magnification, extract_patches)
    except Exception as e:
        pytest.fail(e)


def test_cli_wsi():
    # WSIS = ("CMU-1.ndpi", "", "corrupted.ndpi")
    params = Params()

    params.wsi = f"{BASEDIR}/{WSIS[1]}"
    with pytest.raises(FileNotFoundError):
        cli(wsi, method, annotation, rule, save_to, on_annotation,
            on_foreground, patch_width, patch_height, overlap_width,
            overlap_height, magnification, extract_patches)

    params.wsi = f"{BASEDIR}/{WSIS[2]}"
    with pytest.raises(pyvips.error.Error):
        cli(wsi, method, annotation, rule, save_to, on_annotation,
            on_foreground, patch_width, patch_height, overlap_width,
            overlap_height, magnification, extract_patches)


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

    params.annotation = f"{BASEDIR}/{ANNOTATIONS[3]}"
    with pytest.raises(FileNotFoundError):
        cli(params)


def test_cli_method_annotation_combination():
    # METHODS = ("none", "Classification", "Detection", "Segmentation", "foo")
    """
    ANNOTATIONS = (
        "CMU-1_classification.xml",
        "CMU-1_detection.xml",
        "CMU-1_segmentation.xml",
        "test_emptyfile.txt")
    """
    params = Params()

    # classification and segmentation can share annotation data
    params.method = METHODS[1]
    params.annotation = f"{BASEDIR}/{ANNOTATIONS[2]}""
    cli(params)

    # detection can not share annotation data with other methods
    params.method = METHODS[2]
    params.annotation = f"{BASEDIR}/{ANNOTATIONS[1]}""
    with pytest.raises(FileNotFoundError):
        cli(params)

    params.method = METHODS[2]
    params.annotation = f"{BASEDIR}/{ANNOTATIONS[3]}""
    with pytest.raises(FileNotFoundError):
        cli(params)

    # segmentation can run with classification annotation
    params.method = METHODS[3]
    params.annotation = f"{BASEDIR}/{ANNOTATIONS[1]}""
    with pytest.raises(FileNotFoundError):
        cli(params)


def test_cli_rule():
    """
    RULES = (
        "rule.json",
        "test_emptyfile.txt")
    """
    params = Params()

    params.rule = RULES[1]
    with pytestraises(PermissionError):
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


def test_cli_patch_size():
    # PATCH_SIZES = (256, 0, 1, 0.1, 4096)
    params = Params()

    params.patch_height = PATCH_SIZES[1]
    params.patch_width = PATCH_SIZES[1]
    with pytest.raises(ValueError):
        cli(params)

    params.patch_height = PATCH_SIZES[2]
    params.patch_width = PATCH_SIZES[2]
    with pytest.raises(ValueError):
        cli(params)

    params.patch_height = PATCH_SIZES[3]
    params.patch_width = PATCH_SIZES[3]
    with pytest.raises(ValueError):
        cli(params)

    params.patch_height = PATCH_SIZES[4]
    params.patch_width = PATCH_SIZES[4]
    with pytest.raises(ValueError):
        cli(params)


def test_cli_overlap():
    # OVERLAP_SIZES = (1, 4096, 0, 0.1, 256)
    params = Params()

    params.overlap_height = OVERLAP_SIZES[1]
    with pytest.raises(ValueError):
        cli(params)

    params.overlap_height = OVERLAP_SIZES[2]
    with pytest.raises(ValueError):
        cli(params)

    params.overlap_height = OVERLAP_SIZES[3]
    with pytest.raises(ValueError):
        cli(params)

    params.overlap_height = OVERLAP_SIZES[4]
    with pytest.raises(ValueError):
        cli(params)


def test_cli_on_annotation():
    # ONANNOTATIONS = (1.0, 0, 0.50000000001)
    params = Params()

    params.on_annotation = ONANNOTATIONS[1]
    with pytest.raises(ValueError):
        cli(params)

    params.on_annotation = ONANNOTATIONS[2]
    with pytest.raises(ValueError):
        cli(params)


def test_cli_on_foreground():
    # ONFOREGROUNDS = (1.0, 0, 0.50000000001)
    params = Params()

    params.on_foreground = ONFOREGROUNDS[1]
    with pytest.raises(ValueError):
        cli(params)

    params.on_foreground = ONFOREGROUNDS[2]
    with pytest.raises(ValueError):
        cli(params)


def test_cli_magnification():
    # MAGNIFICATIONS = (10, 1, 80, 40, 20)
    params = Params()

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
