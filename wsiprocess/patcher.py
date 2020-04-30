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
        on_foreground (float, optional): Ratio of overlap area between patches
            and foreground area.
        on_annotation (float, optional): Ratio of overlap area between patches
            and annotation.
        start_sample (bool, optional): Whether to save sample patches on
            Patcher starting.
        finished_sample (bool, optional): Whether to save sample patches on
            Patcher finished its work.
        extract_patches (bool, optional): Whether to save patches when Patcher
            runs.

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
        on_foreground (float): Ratio of overlap area between patches and
            foreground area.
        on_annotation (float): Ratio of overlap area between patches and
            annotation.
        start_sample (bool): Whether to save sample patches on Patcher start.
        finished_sample (bool): Whether to save sample patches on Patcher
            finish.
        extract_patches (bool): Whether to save patches when Patcher runs.

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
            patch_width=256, patch_height=256, overlap_width=1,
            overlap_height=1, on_foreground=0.5, on_annotation=1.,
            start_sample=True, finished_sample=True, extract_patches=True):
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
        self.x_lefttop = [i for i in range(
            0, self.wsi_width, patch_width - overlap_width)][:-1]
        self.y_lefttop = [i for i in range(
            0, self.wsi_height, patch_height - overlap_height)][:-1]
        self.iterator = list(product(self.x_lefttop, self.y_lefttop))
        self.last_x = self.slide.width - patch_width
        self.last_y = self.slide.height - patch_height

        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.extract_patches = extract_patches

        self.on_foreground = on_foreground
        if annotation:
            self.annotation = annotation
            self.masks = annotation.masks
            self.classes = annotation.classes
            self.on_annotation = on_annotation
        else:
            self.annotation = annotation
            self.masks = False
            self.classes = ["none"]
            self.on_annotation = False

        self.save_to = save_to

        self.result = {"result": []}
        self.verify = Verify(save_to, self.filestem, method,
                             start_sample, finished_sample, extract_patches)
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

            bblefts = np.min(coords, axis=1)[:, 0]
            bbtops = np.min(coords, axis=1)[:, 1]
            bbrights = np.max(coords, axis=1)[:, 0]
            bbbottoms = np.max(coords, axis=1)[:, 1]

            # ex : annotation.mask_coords["benign"][0]
            #  = [small_x, small_y, large_x, large_y]
            #  = [bbleft, bbtop, bbright, bbbottom]
            # Bounding boxes with one of its corners on the patch is on the patch.

            patch_left = x
            patch_right = x + self.p_width
            patch_top = y
            patch_bottom = y + self.p_height

            bbleft_right_of_patch_left = set(
                np.where(bblefts >= patch_left)[0])
            bbleft_left_of_patch_right = set(
                np.where(bblefts <= patch_right)[0])
            bbright_right_of_patch_left = set(
                np.where(bbrights >= patch_left)[0])
            bbright_left_of_patch_right = set(
                np.where(bbrights <= patch_right)[0])
            bbtop_below_patch_top = set(np.where(bbtops >= patch_top)[0])
            bbtop_above_patch_bottom = set(np.where(bbtops <= patch_bottom)[0])
            bbbottom_below_patch_top = set(np.where(bbbottoms >= patch_top)[0])
            bbbottom_above_patch_bottom = set(
                np.where(bbbottoms <= patch_bottom)[0])

            bbleft_on_patch = bbleft_right_of_patch_left & bbleft_left_of_patch_right
            bbright_on_patch = bbright_right_of_patch_left & bbright_left_of_patch_right
            bbtop_on_patch = bbtop_above_patch_bottom & bbtop_below_patch_top
            bbbottom_on_patch = bbbottom_above_patch_bottom & bbbottom_below_patch_top

            bb_lefttop_on_patch = bbleft_on_patch & bbtop_on_patch
            bb_leftbottom_on_patch = bbleft_on_patch & bbbottom_on_patch
            bb_righttop_on_patch = bbright_on_patch & bbtop_on_patch
            bb_rightbottom_on_patch = bbright_on_patch & bbbottom_on_patch

            idx_of_bb_on_patch = bb_lefttop_on_patch | bb_leftbottom_on_patch | bb_righttop_on_patch | bb_rightbottom_on_patch

            bbs_raw = coords[list(idx_of_bb_on_patch)]
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

    def save_results(self):
        """Save the extraction results.

        Saves some metadata with the patches results.

        """
        self.result["slide"] = self.filepath
        self.result["method"] = self.method
        self.result["wsi_width"] = self.wsi_width
        self.result["wsi_height"] = self.wsi_height
        self.result["patch_width"] = self.p_width
        self.result["patch_height"] = self.p_height
        self.result["overlap_width"] = self.o_width
        self.result["overlap_hegiht"] = self.o_height
        self.result["start_sample"] = self.start_sample
        self.result["finished_sample"] = self.finished_sample
        self.result["extract_patches"] = self.extract_patches
        self.result["on_foreground"] = self.on_foreground
        self.result["on_annotation"] = self.on_annotation
        self.result["save_to"] = str(Path(self.save_to).absolute())
        self.result["classes"] = self.classes

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
        if self.extract_patches:
            patch = self.slide.slide.crop(x, y, self.p_width, self.p_height)
            for cls in on_annotation_classes:
                patch.jpegsave(
                    "{}/{}/patches/{}/{:06}_{:06}.jpg".format(self.save_to, self.filestem, cls, x, y))
                self.save_patch_result(x, y, cls)

    def get_patch_parallel(self, classes=False, cores=-1):
        """Run get_patch() in parallel.

        Args:
            classes (list): Classes to extract.
            cores (int): Threads to run. -1 means same as the number of cores.
        """
        for cls in classes:
            if self.extract_patches:
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
