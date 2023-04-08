# -*- coding: utf-8 -*-
"""Patcher object to extract patches from whole slide images.
"""

import warnings
import random
from itertools import product
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
import numpy as np
import cv2
from pathlib import Path
import pandas as pd

from .verify import Verify


class Patcher:
    """Patcher object.

    Args:
        slide (wsiprocess.slide.Slide): Slide object.
        method (str): Method name to run. One of {"evaluation",
            "classification", "detection", "segmentation}. Characters are
            converted to lowercase.
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
        on_annotation (float or dict): Ratio of overlap area between patches
            and annotation. dict is also available ex: {"label":value}.
        magnification (int, optional): Magnification of output patches.
        ext (str, optional): Extension of extracted patches.
        start_sample (bool, optional): Whether to save sample patches on
            Patcher starting.
        finished_sample (bool, optional): Whether to save sample patches on
            Patcher finished its work.
        extract_patches (bool, optional): This is deprecated because unless
            "no_patches" is set, Patcher extracts patches.
        no_patches (bool, optional): If set, Patcher runs without extracting
            patches and saves them to disk.
        verbose (bool, optional): If set, a progress bar appears when patching.
        dryrun (bool, optional): Only run patching for first 100 patches.

    Attributes:
        slide (wsiprocess.slide.Slide): Slide object.
        wsi_width (int): Width of the slide.
        wsi_height (int): Height of the slide.
        filepath (str): Path to the whole slide image.
        filestem (str): Stem of the file name.
        method (str): Method name to run. One of {"evaluation",
            "classification", "detection", "segmentation}
        annotation (wsiprocess.annotation.Annotation):
            Annotation object.
        masks (dict): Masks to show the location of classes.
        classes (list): Classes to extract.
        save_to (str): The root of the output directory.
        p_width (int): The width of the cropped patches. It magnification is
            not set, it is same as output patches.
        p_height (int): The height of the cropped patches. It magnification is
            not set, it is same as output patches.
        p_area (int): The area of single patch.
        o_width (int): The width of the overlap areas of patches.
        o_height (int): The height of the overlap areas of patches.
        offset_x (int): The The offset pixels along the x-axis.
        offset_y (int): The The offset pixels along the y-axis.
        on_foreground (float): Ratio of overlap area between patches and
            foreground area.
        on_annotation (float or dict): Ratio of overlap area between patches
            and annotation. dict is also available ex: {"label":value}.
        magnification (int): Magnification of output patches.
        p_scale (float): Ratio of p_width or p_height to output patch size.
        ext (str): Extension of extracted patches.
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): Whether to save patches when Patcher runs.
        no_patches (bool): Whether to save patches when Patcher runs.
        verbose (bool, optional): If set, a progress bar appears when patching.
        dryrun (bool, optional): Only run patching for first 100 patches.

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
            on_annotation=0.5, ext="jpg", magnification=False,
            start_sample=False, finished_sample=False, no_patches=False,
            crop_bbox=False, verbose=False, dryrun=False):
        self.verify = Verify(
            save_to, slide.filestem, method, start_sample, finished_sample,
            no_patches, crop_bbox)
        self.verify.sizes(
            slide.width, slide.height, offset_x, offset_y,
            patch_width, patch_height, overlap_width, overlap_height,
            annotation.dot_bbox_width, annotation.dot_bbox_height)
        self.verify.on_params(on_annotation, on_foreground)
        self.verify.make_dirs()

        self.slide = slide
        self.filepath = slide.filename
        self.filestem = slide.filestem
        self.method = method.lower()
        self.wsi_width = slide.width
        self.wsi_height = slide.height
        self.set_magnification(slide, magnification)
        self.p_width = int(patch_width*self.p_scale)
        self.p_height = int(patch_height*self.p_scale)
        self.p_area = self.p_width * self.p_height
        self.o_width = int(overlap_width)
        self.o_height = int(overlap_height)
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.dot_bbox_width = annotation.dot_bbox_width
        self.dot_bbox_height = annotation.dot_bbox_height
        self.x_lefttop = [i for i in range(
            self.offset_x,
            self.wsi_width,
            patch_width - overlap_width)][:-1]
        self.y_lefttop = [i for i in range(
            self.offset_y,
            self.wsi_height,
            patch_height - overlap_height)][:-1]

        self.last_x = self.slide.width - patch_width
        self.last_y = self.slide.height - patch_height

        self.dryrun = dryrun
        self.get_iterator(dryrun)

        self.ext = ext

        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.no_patches = no_patches

        self.verbose = verbose

        self.on_foreground = on_foreground
        self.annotation = annotation
        if annotation:
            self.masks = annotation.masks
            self.classes = annotation.classes
            if isinstance(on_annotation, (float, int)):
                # if float, apply same threshold value for all classes
                self.on_annotation = {cl: on_annotation for cl in self.classes}
            else:
                self.on_annotation = on_annotation
        else:
            self.masks = False
            self.classes = []
            self.on_annotation = False

        self.save_to = save_to

        self.result = {"result": []}

    def __str__(self):
        return "wsiprocess.patcher.Patcher {}".format(self.slide.path)

    def get_iterator(self, dryrun=False):
        self.iterator = list(product(self.x_lefttop, self.y_lefttop))
        bottomedge = [(x, self.last_y) for x in self.x_lefttop]
        rightedge = [(self.last_x, y) for y in self.y_lefttop]
        rightbottom = [(self.last_x, self.last_y)]
        self.iterator += bottomedge
        self.iterator += rightedge
        self.iterator += rightbottom

        if dryrun:
            self.iterator = self.iterator[:100]

    def set_magnification(self, slide, magnification):
        self.magnification = magnification
        if self.magnification:
            if slide.magnification is None:
                raise KeyError(
                    "{} has no magnification property".format(slide.path))
            if slide.magnification % self.magnification != 0:
                msg = "magnification={} is not a factor of \
                    slide.magnification={}"
                warnings.warn(
                    msg.format(self.magnification, slide.magnification))
            self.p_scale = slide.magnification / self.magnification
        else:
            self.p_scale = 1

    def save_patch_result(self, x, y, cls):
        """Save the extracted patch data to result

        Args:
            x (int): X-axis offset of patch.
            y (int): Y-axis offset of patch.
            cls (str): Class of the patch or the bounding box or the segmented
                area.
        """
        if self.method == "evaluation":
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

        left_on_patch = (patch_left <= bblefts) & (bblefts <= patch_right)
        right_on_patch = (patch_left <= bbrights) & (bbrights <= patch_right)
        top_on_patch = (patch_top <= bbtops) & (bbtops <= patch_bottom)
        bottom_on_patch = (patch_top <= bbbottoms) & (
            bbbottoms <= patch_bottom)

        topleft_on_patch = left_on_patch & top_on_patch
        topright_on_patch = right_on_patch & top_on_patch
        bottomleft_on_patch = left_on_patch & bottom_on_patch
        bottomright_on_patch = right_on_patch & bottom_on_patch

        idx_of_bb_on_patch = topleft_on_patch | topright_on_patch |\
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

        left_on_patch = (patch_left <= bblefts) & (bblefts <= patch_right)
        right_on_patch = (patch_left <= bbrights) & (bbrights <= patch_right)
        top_on_patch = (patch_top <= bbtops) & (bbtops <= patch_bottom)
        bottom_on_patch = (patch_top <= bbbottoms) & (
            bbbottoms <= patch_bottom)

        # One side is on the patch
        leftside_on_patch = (left_on_patch) &\
                            (bbtops <= patch_top) &\
                            (patch_bottom <= bbbottoms)
        rightside_on_patch = (right_on_patch) &\
                             (bbtops <= patch_top) &\
                             (patch_bottom <= bbbottoms)
        topside_on_patch = (bblefts <= patch_left) &\
                           (patch_right <= bbrights) &\
                           (top_on_patch)
        bottomside_on_patch = (bblefts <= patch_left) &\
                              (patch_right <= bbrights) &\
                              (bottom_on_patch)

        # Two sides are on the patch
        leftrightside_on_patch = (left_on_patch) &\
                                 (right_on_patch) &\
                                 (bbtops <= patch_top) &\
                                 (patch_bottom <= bbbottoms)
        topbottomside_on_patch = (bblefts <= patch_left) &\
                                 (patch_right <= bbrights) &\
                                 (top_on_patch) &\
                                 (bottom_on_patch)

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
            patch_mask = self.annotation.get_patch_mask(
                cls, x, y, self.p_width, self.p_height)
            mask_path = "{}/{}/masks/{}/{:06}_{:06}.{}".format(
                self.save_to, self.filestem, cls, x, y, self.ext)
            if not self.no_patches:
                cv2.imwrite(mask_path, patch_mask, (cv2.IMWRITE_PXM_BINARY, 1))
            # contours, _ = cv2.findContours(
            #   patch_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            masks = []
            mask = {"coords": mask_path, "class": cls}
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
        self.result["ext"] = self.ext
        self.result["start_sample"] = self.start_sample
        self.result["finished_sample"] = self.finished_sample
        self.result["no_patches"] = self.no_patches
        self.result["on_foreground"] = self.on_foreground
        self.result["on_annotation"] = self.on_annotation
        self.result["dot_bbox_width"] = self.dot_bbox_width
        self.result["dot_bbox_height"] = self.dot_bbox_height
        self.result["magnification"] = self.magnification
        self.result["dryrun"] = self.dryrun
        self.result["save_to"] = str(Path(self.save_to).absolute())
        self.result["classes"] = sorted(self.classes)

        self.remove_dup_in_results()

        with open(
            "{}/{}/results.json".format(self.save_to, self.filestem),
                "w") as f:
            json.dump(self.result, f, indent=4)

        coords = pd.DataFrame(self.result["result"])
        if not self.result["result"]:
            return

        coords.sort_values(by=["x", "y"], inplace=True)
        coords.reset_index(drop=True, inplace=True)
        if self.method == "classification":
            for cls in self.classes:
                coords[cls] = (coords["class"] == cls)

            # aggregate if a patch has multiple classes
            if coords.duplicated(subset=["x", "y", "w", "h"]).sum() > 0:
                dup_to_keep = ~coords.duplicated(
                    subset=["x", "y", "w", "h"], keep="first")

                for i, row in coords[dup_to_keep].iterrows():
                    dup_x = coords.x == row.x
                    dup_y = coords.y == row.y
                    dup_w = coords.w == row.w
                    dup_h = coords.h == row.h
                    dup = coords[dup_x & dup_y & dup_w & dup_h]
                    coords.loc[i, self.classes] = dup[self.classes].any()

                coords.drop_duplicates(
                    subset=["x", "y", "w", "h"], keep="first", inplace=True)

            coords.drop(columns="class", inplace=True)

        elif self.method == "detection":
            # column name: bbs
            # not implemented
            pass

        elif self.method == "segmentation":
            # column name: masks
            for cls in self.classes:
                coords[cls] = False

            def mask_cls_to_column(x):
                for mask in x.masks:
                    coords.loc[x.name, mask["class"]] = True

            coords.apply(mask_cls_to_column, axis=1)

        coords.to_csv(
            "{}/{}/coords.csv".format(self.save_to, self.filestem),
            index=None)

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
        for cls in on_annotation_classes:
            if not self.no_patches:
                patch = self.crop_patch(x, y)
                self.save_patch(patch, "{}/{}/patches/{}/{:06}_{:06}.{}".format(
                    self.save_to, self.filestem, cls, x, y, self.ext))
            self.save_patch_result(x, y, cls)

    def get_patch_parallel(self, classes=False, max_workers=-1):
        """Run get_patch() in parallel.

        Args:
            classes (list): Classes to extract.
            max_workers (int): Workers to run. -1 runs with cores*5 threads.
        """
        for cls in classes:
            assert cls in self.on_annotation, f"on_annotation of {cls} not set"

        if max_workers == 0 | max_workers < -1:
            msg = "max_workers must be 1 or larger, or -1"
            msg += f", got {max_workers}"
            warnings.warn(msg)
        for cls in classes:
            if not self.no_patches:
                self.verify.make_dir(
                    "{}/{}/patches/{}".format(
                        self.save_to, self.filestem, cls))
                if self.method == "segmentation":
                    self.verify.make_dir(
                        "{}/{}/masks/{}".format(
                            self.save_to, self.filestem, cls))

        if self.start_sample:
            self.get_random_sample("start", 3)

        if max_workers == -1:
            max_workers = os.cpu_count()*5
        else:
            max_workers = max_workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for x, y in self.iterator:
                futures.append(
                    executor.submit(
                        self.get_patch,
                        *(x, y, classes)
                    )
                )
            if self.verbose:
                desc = f"[{self.filepath} {self.p_width}x{self.p_height}]"
                [_ for _ in tqdm(
                    as_completed(futures),
                    desc=desc,
                    total=len(futures))]

        # save results
        self.save_results()

        if self.finished_sample:
            self.get_random_sample("finished", 3)

    def get_mini_patch_parallel(self, classes=False):
        for cls in classes:
            self.verify.make_dir(
                "{}/{}/mini_patches/{}".format(
                    self.save_to, self.filestem, cls))

        for patch in self.result["result"]:
            for bb in patch["bbs"]:
                if bb["class"] not in classes:
                    continue
                # not properly works with the magnification settings
                mini_patch = self.crop_patch(
                    patch["x"] + bb["x"],
                    patch["y"] + bb["y"],
                    bb["w"],
                    bb["h"]
                )
                self.save_patch(
                    mini_patch,
                    "{}/{}/mini_patches/{}/{:06}_{:06}.{}".format(
                        self.save_to, self.filestem,
                        bb["class"],
                        patch["x"] + bb["x"],
                        patch["y"] + bb["y"],
                        self.ext))

    def patch_on_foreground(self, x, y):
        """Check if the patch is on the foreground area.

        Args:
            x (int): X-axis offset of a patch.
            y (int): Y-axis offset of a patch.

        Returns:
            (bool): Whether the patch is on the foreground area.
        """
        patch_mask = self.annotation.get_patch_mask(
            "foreground", x, y, self.p_width, self.p_height)
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
        patch_mask = self.annotation.get_patch_mask(
            cls, x, y, self.p_width, self.p_height)
        return (patch_mask.sum() / self.p_area) >= self.on_annotation[cls]

    def get_random_sample(self, phase, sample_count=1):
        """Get random patch to check if the patcher can work properly.

        Args:
            phase (str): When to check. One of {start, finish}
            sample_count (int): Number of patches to extract.
        """
        for i in range(sample_count):
            x = random.choice(self.x_lefttop)
            y = random.choice(self.y_lefttop)
            patch = self.crop_patch(x, y)
            self.save_patch(patch, "{}/{}/{}_sample/{:06}_{:06}.{}".format(
                self.save_to, self.filestem, phase, x, y, self.ext))

    def crop_patch(self, x, y, w=False, h=False):
        if not w:
            w = self.p_width
        if not h:
            h = self.p_height
        return self.slide.crop(x, y, w, h)

    def save_patch(self, patch, save_as):
        if patch.mode == "RGBA" and self.ext == "jpg":
            warnings.warn(
                "patch has RGBA data. Discarding alpha to save as jpg")
            patch = patch.convert("RGB")

        if self.magnification:
            patch = patch.resize((
                int(self.p_width//self.p_scale),
                int(self.p_height//self.p_scale)
            ))

        patch.save(save_as)
