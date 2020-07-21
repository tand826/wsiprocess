# -*- coding: utf-8 -*-
"""Patcher object to extract patches from whole slide images.
"""

import random
from itertools import product
import json
from joblib import Parallel, delayed
import numpy as np
import cv2
from pathlib import Path

from .verify import Verify


difpatches = {'2019-11-27 09.33.45_036864_038912', '2019-11-27 09.33.45_034304_037376', '2019-11-27 09.33.45_056832_044544', '2019-11-27 09.33.45_063488_010752', '2019-11-27 09.33.45_035328_037376', '2019-11-27 09.33.45_044032_039936', '2019-11-27 09.33.45_037888_039424', '2019-11-27 09.33.45_062976_009728', '2019-11-27 09.33.45_033280_019968', '2019-11-27 09.33.45_038400_037888', '2019-11-27 09.33.45_052224_020480', '2019-11-27 09.33.45_017408_039424', '2019-11-27 09.33.45_034304_036864', '2019-11-27 09.33.45_044544_039936', '2019-11-27 09.33.45_047616_015872', '2019-11-27 09.33.45_066048_011776', '2019-11-27 09.33.45_054784_041984', '2019-11-27 09.33.45_016896_039936', '2019-11-27 09.33.45_042496_038400', '2019-11-27 09.33.45_021504_025088', '2019-11-27 09.33.45_046592_038912', '2019-11-27 09.33.45_041472_040448', '2019-11-27 09.33.45_048128_015872', '2019-11-27 09.33.45_015872_039936', '2019-11-27 09.33.45_048128_016384', '2019-11-27 09.33.45_044032_016896', '2019-11-27 09.33.45_035840_036864', '2019-11-27 09.33.45_054272_042496', '2019-11-27 09.33.45_035328_040960', '2019-11-27 09.33.45_027136_036864', '2019-11-27 09.33.45_035328_038912', '2019-11-27 09.33.45_033792_037376', '2019-11-27 09.33.45_016384_039936', '2019-11-27 09.33.45_034816_037376', '2019-11-27 09.33.45_036864_039424', '2019-11-27 09.33.45_037888_038400', '2019-11-27 09.33.45_049664_038912', '2019-11-27 09.33.45_036864_040448', '2019-11-27 09.33.45_036352_039424', '2019-11-27 09.33.45_013312_040960', '2019-11-27 09.33.45_050688_039936', '2019-11-27 09.33.45_028672_037888', '2019-11-27 09.33.45_044032_016384', '2019-11-27 09.33.45_033792_036864', '2019-11-27 09.33.45_036864_039936', '2019-11-27 09.33.45_013312_041472', '2019-11-27 09.33.45_064512_010752', '2019-11-27 09.33.45_052224_022016', '2019-11-27 09.33.45_035328_039424', '2019-11-27 09.33.45_038400_038912', '2019-11-27 09.33.45_063488_010240', '2019-11-27 09.33.45_015360_040960', '2019-11-27 09.33.45_032768_037888', '2019-11-27 09.33.45_041472_039424', '2019-11-27 09.33.45_014336_040960', '2019-11-27 09.33.45_027136_024576', '2019-11-27 09.33.45_035840_037376', '2019-11-27 09.33.45_032256_037376', '2019-11-27 09.33.45_030720_014336', '2019-11-27 09.33.45_015360_039936', '2019-11-27 09.33.45_061952_008704', '2019-11-27 09.33.45_037376_040960', '2019-11-27 09.33.45_037376_038400', '2019-11-27 09.33.45_037888_037376', '2019-11-27 09.33.45_043520_016896', '2019-11-27 09.33.45_060928_008192', '2019-11-27 09.33.45_019968_038912', '2019-11-27 09.33.45_037376_036864', '2019-11-27 09.33.45_048640_016896', '2019-11-27 09.33.45_033280_019456', '2019-11-27 09.33.45_021504_025600', '2019-11-27 09.33.45_063488_011264', '2019-11-27 09.33.45_064512_010240', '2019-11-27 09.33.45_043520_013312', '2019-11-27 09.33.45_036864_038400', '2019-11-27 09.33.45_045056_014336', '2019-11-27 09.33.45_036352_036864', '2019-11-27 09.33.45_057344_045056', '2019-11-27 09.33.45_007168_018944', '2019-11-27 09.33.45_045568_009216', '2019-11-27 09.33.45_036352_037376', '2019-11-27 09.33.45_054272_041984', '2019-11-27 09.33.45_020480_038912', '2019-11-27 09.33.45_041984_039424', '2019-11-27 09.33.45_007168_018432', '2019-11-27 09.33.45_049664_039936', '2019-11-27 09.33.45_035840_039936', '2019-11-27 09.33.45_014336_041472', '2019-11-27 09.33.45_026112_024064', '2019-11-27 09.33.45_034816_037888', '2019-11-27 09.33.45_057344_044032', '2019-11-27 09.33.45_037376_037888', '2019-11-27 09.33.45_030720_013824', '2019-11-27 09.33.45_043520_016384', '2019-11-27 09.33.45_038400_039424', '2019-11-27 09.33.45_045056_039936', '2019-11-27 09.33.45_037376_037376', '2019-11-27 09.33.45_021504_038912', '2019-11-27 09.33.45_049152_015872', '2019-11-27 09.33.45_038400_038400', '2019-11-27 09.33.45_035840_039424', '2019-11-27 09.33.45_005120_018432', '2019-11-27 09.33.45_018432_025088', '2019-11-27 09.33.45_026624_037376', '2019-11-27 09.33.45_029696_022016', '2019-11-27 09.33.45_040960_039424', '2019-11-27 09.33.45_037376_039936', '2019-11-27 09.33.45_023552_037376', '2019-11-27 09.33.45_036352_037888', '2019-11-27 09.33.45_036864_037376', '2019-11-27 09.33.45_025600_025088', '2019-11-27 09.33.45_046592_039424', '2019-11-27 09.33.45_039936_038912', '2019-11-27 09.33.45_035840_038912', '2019-11-27 09.33.45_025600_037888', '2019-11-27 09.33.45_030720_019968', '2019-11-27 09.33.45_049152_039424', '2019-11-27 09.33.45_060928_008704', '2019-11-27 09.33.45_033280_036864', '2019-11-27 09.33.45_037376_040448', '2019-11-27 09.33.45_023552_037888', '2019-11-27 09.33.45_048640_038912', '2019-11-27 09.33.45_050176_039936', '2019-11-27 09.33.45_053760_042496', '2019-11-27 09.33.45_053248_041472', '2019-11-27 09.33.45_065024_009216', '2019-11-27 09.33.45_049152_038912', '2019-11-27 09.33.45_036864_036864', '2019-11-27 09.33.45_035328_036864', '2019-11-27 09.33.45_031744_013312', '2019-11-27 09.33.45_029184_036864', '2019-11-27 09.33.45_036864_037888', '2019-11-27 09.33.45_025600_037376', '2019-11-27 09.33.45_024576_037376', '2019-11-27 09.33.45_042496_040448', '2019-11-27 09.33.45_037376_038912', '2019-11-27 09.33.45_033280_020480', '2019-11-27 09.33.45_032768_011264', '2019-11-27 09.33.45_037376_039424', '2019-11-27 09.33.45_036352_038400'}


class Patcher:
    """Patcher object.

    Args:
        slide (wsiprocess.slide.Slide): Slide object.
        method (str): Method name to run. One of {"none", "classification",
            "detection", "segmentation}. Characters are converted to lowercase.
        annotation (wsiprocess.annotation.Annotation, optional):
            Annotation object.
        save_to (str, optional): The root of the output directory.
        patch_width (int, optional): The width of the output patches.
        patch_height (int, optional): The height of the output patches.
        overlap_width (int, optional): The width of the overlap areas of
            patches.
        overlap_height (int, optional): The height of the overlap areas of
            patches.
        offset_x (int, optional): The offset pixels along the x-axis.
        offset_y (int, optional): The offset pixels along the y-axis.
        on_foreground (float, optional): Ratio of overlap area between patches
            and foreground area.
        on_annotation (float, optional): Ratio of overlap area between patches
            and annotation.
        start_sample (bool, optional): Whether to save sample patches on
            Patcher starting.
        finished_sample (bool, optional): Whether to save sample patches on
            Patcher finished its work.
        extract_patches (bool, optional): This is deprecated because unless
            "no_patches" is set, Patcher extracts patches.
        no_patches (bool, optional): If set, Patcher runs without extracting
            patches and saves them to disk.

    Attributes:
        slide (wsiprocess.slide.Slide): Slide object.
        wsi_width (int): Width of the slide.
        wsi_height (int): Height of the slide.
        filepath (str): Path to the whole slide image.
        filestem (str): Stem of the file name.
        method (str): Method name to run. One of {"none", "classification",
            "detection", "segmentation}
        annotation (wsiprocess.annotation.Annotation):
            Annotation object.
        masks (dict): Masks to show the location of classes.
        classes (list): Classes to extract.
        save_to (str): The root of the output directory.
        p_width (int): The width of the output patches.
        p_height (int): The height of the output patches.
        p_area (int): The area of single patch.
        o_width (int): The width of the overlap areas of patches.
        o_height (int): The height of the overlap areas of patches.
        offset_x (int): The The offset pixels along the x-axis.
        offset_y (int): The The offset pixels along the y-axis.
        on_foreground (float): Ratio of overlap area between patches and
            foreground area.
        on_annotation (float): Ratio of overlap area between patches and
            annotation.
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): Whether to save patches when Patcher runs.
        no_patches (bool): Whether to save patches when Patcher runs.

        x_lefttop (list): Offsets of patches to the x-axis direction except for
            the right edge.
        y_lefttop (list): Offsets of patches to the y-axis direction except for
            the bottom edge.
        iterator (list):  Offset coordinates of patches.
        last_x (int): X-axis offset of the right edge patch.
        last_y (int): Y-axis offset of the right edge patch.

        result (dict): Temporary storage for the computed result of patches.
    """

    def __init__(
            self, slide, method, annotation=False, save_to=".",
            patch_width=256, patch_height=256, overlap_width=0,
            overlap_height=0, offset_x=0, offset_y=0, on_foreground=0.5,
            on_annotation=1., start_sample=True, finished_sample=True,
            no_patches=False):
        Verify.verify_sizes(
            slide.wsi_width, slide.wsi_height, patch_width, patch_height,
            overlap_width, overlap_height)
        self.slide = slide
        self.filepath = slide.filename
        self.filestem = slide.filestem
        self.method = method.lower()
        self.wsi_width = slide.wsi_width
        self.wsi_height = slide.wsi_height
        self.p_width = int(patch_width)
        self.p_height = int(patch_height)
        self.p_area = patch_width * patch_height
        self.o_width = int(overlap_width)
        self.o_height = int(overlap_height)
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.x_lefttop = [i for i in range(
            self.offset_x, self.wsi_width, patch_width - overlap_width)][:-1]
        self.y_lefttop = [i for i in range(
            self.offset_y, self.wsi_height, patch_height - overlap_height)][:-1]
        self.iterator = list(product(self.x_lefttop, self.y_lefttop))
        self.last_x = self.slide.width - patch_width
        self.last_y = self.slide.height - patch_height

        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.no_patches = no_patches

        self.on_foreground = on_foreground
        self.annotation = annotation
        if annotation:
            self.masks = annotation.masks
            self.classes = annotation.classes
            self.on_annotation = on_annotation
        else:
            self.masks = False
            self.classes = ["none"]
            self.on_annotation = False

        self.save_to = save_to

        self.result = {"result": []}
        self.verify = Verify(save_to, self.filestem, method,
                             start_sample, finished_sample, no_patches)
        self.verify.verify_dirs()

    def __str__(self):
        return "wsiprocess.patcher.Patcher {}".format(self.slide.filename)

    def save_patch_result(self, x, y, cls):
        """Save the extracted patch data to result

        Args:
            x (int): X-axis offset of patch.
            y (int): Y-axis offset of patch.
            cls (str): Class of the patch or the bounding box or the segmented
                area.
        """
        if self.method == "none":
            self.result["result"].append({"x": x,
                                          "y": y,
                                          "w": self.p_width,
                                          "h": self.p_height})

        elif self.method == "classification":
            self.result["result"].append({"x": x,
                                          "y": y,
                                          "w": self.p_width,
                                          "h": self.p_height,
                                          "class": cls})

        elif self.method == "detection":
            bbs = []
            for cls in self.classes:
                for bb in self.find_bbs(x, y, cls):
                    bbs.append({"x": bb["x"],
                                "y": bb["y"],
                                "w": bb["w"],
                                "h": bb["h"],
                                "class": bb["class"]})
            if bbs:
                self.result["result"].append({"x": x,
                                              "y": y,
                                              "w": self.p_width,
                                              "h": self.p_height,
                                              "bbs": bbs})

        elif self.method == "segmentation":
            masks = []
            for cls in self.classes:
                for mask in self.find_masks(x, y, cls):
                    masks.append({"coords": mask["coords"],
                                  "class": mask["class"]})
            self.result["result"].append({"x": x,
                                          "y": y,
                                          "w": self.p_width,
                                          "h": self.p_height,
                                          "masks": masks})

        else:
            raise NotImplementedError

    def find_bbs(self, x, y, cls):
        """Find bounding boxes which are on the patch.

        Bounding boxes with one of its corners on the patch is on the patch.
            ex : annotation.mask_coords["benign"][0]
             = [small_x, small_y, large_x, large_y]
             = [bbleft, bbtop, bbright, bbbottom]

        TODO:
            This function can not handle like the case that the annotation is
            covering the whole area of the patch or the case that one of the
            side of annotation is striding over the patch.

        Args:
            x (int): X-axis offset of patch.
            y (int): Y-axis offset of patch.
            cls (str): Class of the patch or the bounding box or the segmented
                area.

        """
        if not self.patch_on_annotation(cls, x, y):
            return []
        else:
            # Find bounding boxes which are on the patch
            if cls == "foreground":
                return []
            coords = self.annotation.mask_coords[cls]
            for idx, coord in enumerate(coords):
                if len(coord) != 4:
                    coords[idx] = self.to_bb(coord)
            coords = np.array(coords)

            idx_of_bb_on_patch = self.corner_on_patch(coords, x, y)
            idx_of_bb_on_patch += self.side_on_patch(coords, x, y)
            idx_of_bb_on_patch += self.annotation_cover_patch(coords, x, y)

            idx_of_bb_on_patch = list(set(idx_of_bb_on_patch))

            bbs_raw = coords[idx_of_bb_on_patch]
            bbs = []
            for bb_raw in bbs_raw:
                x1 = bb_raw[:, 0].min()
                y1 = bb_raw[:, 1].min()
                x2 = bb_raw[:, 0].max()
                y2 = bb_raw[:, 1].max()
                bbx = int(max(x1 - x, 0))
                bby = int(max(y1 - y, 0))
                bbw = int(min(x2 - x1 + bbx, self.p_width)) - bbx
                bbh = int(min(y2 - y1 + bby, self.p_height)) - bby
                bb = {"x": bbx,
                      "y": bby,
                      "w": bbw,
                      "h": bbh,
                      "class": cls}
                bbs.append(bb)
            return bbs

    def corner_on_patch(self, coords, x, y):
        """Check if at least one of the corners is on the patch.

        Args:
            coords (np.array) : Coordinations of annotations.
            px (int) : X coordinate of left top corner of the patch.
            py (int) : Y coordinate of left top corner of the patch.

        Returns:
            idx_of_bb_on_patch (list): List of np.int64s which are the indices
                of bounding boxes on the patch.
        """
        bblefts = np.min(coords, axis=1)[:, 0]
        bbtops = np.min(coords, axis=1)[:, 1]
        bbrights = np.max(coords, axis=1)[:, 0]
        bbbottoms = np.max(coords, axis=1)[:, 1]

        patch_left = x
        patch_right = x + self.p_width
        patch_top = y
        patch_bottom = y + self.p_height

        topleft_on_patch = (patch_left <= bblefts) &\
                           (bblefts <= patch_right) &\
                           (patch_top <= bbtops) &\
                           (bbtops <= patch_bottom)
        topright_on_patch = (patch_left <= bbrights) &\
                            (bbrights <= patch_right) &\
                            (patch_top <= bbtops) &\
                            (bbtops <= patch_top)
        bottomleft_on_patch = (patch_left <= bblefts) &\
                              (bblefts <= patch_right) &\
                              (patch_top <= bbbottoms) &\
                              (bbbottoms <= patch_bottom)
        bottomright_on_patch = (patch_left <= bbrights) &\
                               (bbrights <= patch_right) &\
                               (patch_top <= bbbottoms) &\
                               (bbbottoms <= patch_bottom)

        idx_of_bb_on_patch = topleft_on_patch | topright_on_patch | \
            bottomleft_on_patch | bottomright_on_patch
        idx_of_bb_on_patch = np.where(idx_of_bb_on_patch)[0]
        return list(idx_of_bb_on_patch)

    def side_on_patch(self, coords, x, y):
        """Check if at least one of the side is on the patch.

        Args:
            coords (np.array) : Coordinations of annotations.
            px (int) : X coordinate of left top corner of the patch.
            py (int) : Y coordinate of left top corner of the patch.

        Returns:
            idx_of_bb_on_patch (list): List of np.int64s which are the indices
                of bounding boxes on the patch.
        """
        bblefts = np.min(coords, axis=1)[:, 0]
        bbtops = np.min(coords, axis=1)[:, 1]
        bbrights = np.max(coords, axis=1)[:, 0]
        bbbottoms = np.max(coords, axis=1)[:, 1]

        patch_left = x
        patch_right = x + self.p_width
        patch_top = y
        patch_bottom = y + self.p_height

        # One side is on the patch
        leftside_on_patch = (patch_left <= bblefts) &\
                            (bblefts <= patch_right) &\
                            (bbtops <= patch_top) &\
                            (patch_bottom <= bbbottoms)
        rightside_on_patch = (patch_left <= bbrights) &\
                             (bbrights <= patch_right) &\
                             (bbtops <= patch_top) &\
                             (patch_bottom <= bbbottoms)
        topside_on_patch = (bblefts <= patch_left) &\
                           (patch_right <= bbrights) &\
                           (patch_top <= bbtops) &\
                           (bbtops <= patch_bottom)
        bottomside_on_patch = (bblefts <= patch_left) &\
                              (patch_right <= bbrights) &\
                              (patch_top <= bbbottoms) &\
                              (bbbottoms <= patch_bottom)

        # Two side is on the patch
        leftrightside_on_patch = (patch_left <= bblefts) &\
                                 (bblefts <= patch_right) &\
                                 (patch_left <= bbrights) &\
                                 (bbrights <= patch_right) &\
                                 (bbtops <= patch_top) &\
                                 (patch_bottom <= bbbottoms)
        topbottomside_on_patch = (bblefts <= patch_left) &\
                                 (patch_right <= bbrights) &\
                                 (patch_top <= bbtops) &\
                                 (bbtops <= patch_bottom) &\
                                 (patch_top <= bbbottoms) &\
                                 (bbbottoms <= patch_bottom)

        idx_of_bb_on_patch = leftside_on_patch | rightside_on_patch | \
            topside_on_patch | bottomside_on_patch | \
            leftrightside_on_patch | topbottomside_on_patch
        idx_of_bb_on_patch = np.where(idx_of_bb_on_patch)[0]
        idx_of_bb_on_patch = list(set(idx_of_bb_on_patch))
        return list(idx_of_bb_on_patch)

    def annotation_cover_patch(self, coords, x, y):
        """Check if the annotation is covering the whole patch.

        Args:
            coords (np.array) : Coordinations of annotations.
            px (int) : X coordinate of left top corner of the patch.
            py (int) : Y coordinate of left top corner of the patch.

        Returns:
            idx_of_bb_on_patch (list): List of np.int64s which are the indices
                of bounding boxes on the patch.
        """
        bblefts = np.min(coords, axis=1)[:, 0]
        bbtops = np.min(coords, axis=1)[:, 1]
        bbrights = np.max(coords, axis=1)[:, 0]
        bbbottoms = np.max(coords, axis=1)[:, 1]

        patch_left = x
        patch_right = x + self.p_width
        patch_top = y
        patch_bottom = y + self.p_height

        idx_of_bb_on_patch = (bblefts <= patch_left) &\
                             (patch_right <= bbrights) &\
                             (bbtops <= patch_top) &\
                             (patch_bottom <= bbbottoms)
        idx_of_bb_on_patch = np.where(idx_of_bb_on_patch)[0]
        return list(idx_of_bb_on_patch)

    def to_bb(self, coord):
        """Convert coordinates to voc coordinates.

        Args:
            coord (list): List of coordinates stored as below::

                [[xOfOneCorner, yOfOneCorner],
                 [xOfApex,      yOfApex]]

        Returns:
            outer_coord (list): List of coordinates stored as below::

                [[xmin, ymin],
                 [xmin, ymax],
                 [xmax, ymax],
                 [xmax, ymin]]

        """
        coord = np.array(coord)
        xmin, ymin = np.min(coord, axis=0)
        xmax, ymax = np.max(coord, axis=0)
        outer_coord = [[xmin, ymin],
                       [xmin, ymax],
                       [xmax, ymax],
                       [xmax, ymin]]
        return outer_coord

    def find_masks(self, x, y, cls):
        """Get the masked area corresponding to the given patch area.

        Args:
            x (int): X-axis offset of a patch.
            y (int): Y-axis offset of a patch.
            cls (str): Class of the patch or the bounding box or the segmented
                area.

        Returns:
            masks (list): List containing a dict of coords and its class. This
                coords is a path to the png image.
        """
        if not self.patch_on_annotation(cls, x, y):
            return []
        else:
            # Find mask coords
            patch_mask = self.masks[cls][y:y+self.p_height, x:x+self.p_width]
            mask_png_path = "{}/{}/masks/{}/{:06}_{:06}.png".format(
                self.save_to, self.filestem, cls, x, y)
            cv2.imwrite(mask_png_path, patch_mask, (cv2.IMWRITE_PXM_BINARY, 1))
            # contours, _ = cv2.findContours(patch_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            masks = []
            mask = {"coords": mask_png_path, "class": cls}
            masks.append(mask)
            return masks

    def remove_dup_in_results(self):
        """Remove duplicate results in self.result["results"]
        """
        results = set()
        for result in self.result["result"]:
            results.add(json.dumps(result))
        self.result["result"] = [json.loads(res) for res in list(results)]

    def save_results(self):
        """Save the extraction results.

        Saves some metadata with the patches results.

        """
        self.result["slide"] = self.slide.path
        self.result["method"] = self.method
        self.result["wsi_width"] = self.wsi_width
        self.result["wsi_height"] = self.wsi_height
        self.result["patch_width"] = self.p_width
        self.result["patch_height"] = self.p_height
        self.result["overlap_width"] = self.o_width
        self.result["overlap_hegiht"] = self.o_height
        self.result["offset_x"] = self.offset_x
        self.result["offset_y"] = self.offset_y
        self.result["start_sample"] = self.start_sample
        self.result["finished_sample"] = self.finished_sample
        self.result["no_patches"] = self.no_patches
        self.result["on_foreground"] = self.on_foreground
        self.result["on_annotation"] = self.on_annotation
        self.result["save_to"] = str(Path(self.save_to).absolute())
        self.result["classes"] = sorted(self.classes)

        self.remove_dup_in_results()

        with open("{}/{}/results.json".format(self.save_to, self.filestem), "w") as f:
            json.dump(self.result, f, indent=4)

    def get_patch(self, x, y, classes=False):
        """Extract a single patch.

        Args:
            x (int): X-axis offset of a patch.
            y (int): Y-axis offset of a patch.
            classes (list): For the case of method is classification, extract
                the patch for multiple times if the patch is on the border of
                two or more classes. To prevent patcher to extract a single
                patch for multiple classes, `on_annotation=1.0` should work.
        """
        if self.on_foreground:
            if not self.patch_on_foreground(x, y):
                return
        if self.on_annotation:
            on_annotation_classes = []
            for cls in classes:
                if self.patch_on_annotation(cls, x, y):
                    on_annotation_classes.append(cls)
        else:
            on_annotation_classes = ["foreground"]
        patch = self.slide.slide.crop(x, y, self.p_width, self.p_height)
        for cls in on_annotation_classes:
            if not self.no_patches:
                patch.jpegsave(
                    "{}/{}/patches/{}/{:06}_{:06}.jpg".format(
                        self.save_to, self.filestem, cls, x, y))
            self.save_patch_result(x, y, cls)

    def get_patch_parallel(self, classes=False, cores=-1):
        """Run get_patch() in parallel.

        Args:
            classes (list): Classes to extract.
            cores (int): Threads to run. -1 means same as the number of cores.
        """
        for cls in classes:
            if not self.no_patches:
                self.verify.verify_dir(
                    "{}/{}/patches/{}".format(self.save_to, self.filestem, cls))
            if self.method == "segmentation":
                self.verify.verify_dir(
                    "{}/{}/masks/{}".format(self.save_to, self.filestem, cls))

        if self.start_sample:
            self.get_random_sample("start", 3)

        parallel = Parallel(n_jobs=cores, backend="threading", verbose=0)
        # from the left top to just before the right bottom.
        parallel([delayed(self.get_patch)(x, y, classes)
                  for x, y in self.iterator])
        # the bottom edge.
        parallel([delayed(self.get_patch)(x, self.last_y, classes)
                  for x in self.x_lefttop])
        # the right edge
        parallel([delayed(self.get_patch)(self.last_x, y, classes)
                  for y in self.y_lefttop])
        # right bottom patch
        self.get_patch(self.last_x, self.last_y, classes)

        # save results
        self.save_results()

        if self.finished_sample:
            self.get_random_sample("finished", 3)

    def patch_on_foreground(self, x, y):
        """Check if the patch is on the foreground area.

        Args:
            x (int): X-axis offset of a patch.
            y (int): Y-axis offset of a patch.

        Returns:
            (bool): Whether the patch is on the foreground area.
        """
        patch_mask = self.masks["foreground"][y:y +
                                              self.p_height, x:x+self.p_width]
        return (patch_mask.sum() / self.p_area) >= self.on_foreground

    def patch_on_annotation(self, cls, x, y):
        """Check if the patch is on the annotation area of a class.

        Args:
            cls (str): Class of the patch or the bounding box or the segmented
                area.
            x (int): X-axis offset of a patch.
            y (int): Y-axis offset of a patch.

        Returns:
            (bool): Whether the patch is on the anntation.
        """
        patch_mask = self.masks[cls][y:y+self.p_height, x:x+self.p_width]
        return (patch_mask.sum() / self.p_area) >= self.on_annotation

    def get_random_sample(self, phase, sample_count=1):
        """Get random patch to check if the patcher can work properly.

        Args:
            phase (str): When to check. One of {start, finish}
            sample_count (int): Number of patches to extract.
        """
        for i in range(sample_count):
            x = random.choice(self.x_lefttop)
            y = random.choice(self.y_lefttop)
            patch = self.slide.slide.crop(x, y, self.p_width, self.p_height)
            patch.pngsave(
                "{}/{}/{}_sample/{:06}_{:06}.png".format(self.save_to, self.filestem, phase, x, y))
