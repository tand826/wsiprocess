import random
from joblib import Parallel, delayed
from itertools import product
import json

from .verify import Verify


class Patcher:

    def __init__(self, slide, method, annotation=False, save_to=".", patch_width=256, patch_height=256,
                 overlap_width=1, overlap_height=1, on_foreground=1., on_annotation=1.,
                 start_sample=True, finished_sample=True, extract_patches=True):
        self.slide = slide
        self.filepath = slide.filename
        self.filestem = slide.filestem
        self.method = method
        self.wsi_width = slide.wsi_width
        self.wsi_height = slide.wsi_height
        self.p_width = patch_width
        self.p_height = patch_height
        self.p_area = patch_width * patch_height
        self.o_width = overlap_width
        self.o_height = overlap_height
        self.x_lefttop = [i for i in range(0, self.wsi_width, patch_width - overlap_width)][:-1]
        self.y_lefttop = [i for i in range(0, self.wsi_height, patch_height - overlap_height)][:-1]
        self.iterator = product(self.x_lefttop, self.y_lefttop)
        self.last_x = self.slide.width - patch_width
        self.last_y = self.slide.height - patch_height

        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.extract_patches = extract_patches

        if annotation:
            self.annotation = annotation
            self.masks = annotation.masks
            self.classes = annotation.classes
            self.on_foreground = on_foreground
            self.on_annotation = on_annotation
        else:
            self.annotation = False
            self.masks = False
            self.classes = False
            self.on_foreground = False
            self.on_annotation = False

        self.save_to = save_to

        self.result = {"result": []}

        self.verify = Verify(save_to, self.filestem, method,
                             start_sample, finished_sample, extract_patches)
        self.verify.verify_dirs()

    def save_patch_result(self, x, y, cls):
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
            for bb in self.find_bbs(x, y):
                bbs.append({"x": bb["x"],
                            "y": bb["y"],
                            "w": bb["width"],
                            "h": bb["height"],
                            "class": bb["class"]})
            self.result["result"].append({"x": x,
                                          "y": y,
                                          "w": self.p_width,
                                          "h": self.p_height,
                                          "bbs": bbs})

        elif self.method == "segmentation":
            masks = []
            for mask in self.find_masks(x, y):
                masks.append({"coords": mask["coords"],
                              "class": mask["class"]})
            self.result["result"] = {"x": x,
                                     "y": y,
                                     "w": self.p_width,
                                     "h": self.p_height,
                                     "masks": masks}

        else:
            raise NotImplementedError

    def find_bbs(self, x, y, cls=False):
        pass

    def find_masks(self, x, y, cls=False):
        pass

    def save_results(self):
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

        with open("{}/{}/results.json", "w") as f:
            json.dump(self.result, f)

    def get_patch(self, x, y, cls=False):
        if self.on_foreground:
            if not self.patch_on_foreground(x, y):
                return
        if self.on_annotation:
            if not self.patch_on_annotation(cls, x, y):
                return
        if self.extract_patches:
            patch = self.slide.slide.crop(x, y, self.p_width, self.p_height)
            patch.pngsave("{}/{}/patches/{}/{:06}_{:06}.png".format(self.save_to, self.filestem, cls, x, y))
        self.save_patch_result(x, y, cls)

    def get_patch_parallel(self, cls=False, cores=-1):
        if self.extract_patches:
            self.verify.verify_dir("{}/{}/patches/{}".format(self.save_to, self.filestem, cls))

        if self.start_sample:
            self.get_random_sample("start", 3)

        parallel = Parallel(n_jobs=cores, backend="threading", verbose=1)

        # from the left top to just before the right bottom.
        parallel([delayed(self.get_patch)(x, y, cls) for x, y in self.iterator])

        # the bottom edge.
        parallel([delayed(self.get_patch)(x, self.last_y, cls) for x in self.x_lefttop])

        # the right edge
        parallel([delayed(self.get_patch)(self.last_x, y, cls) for y in self.y_lefttop])

        # right bottom patch
        self.get_patch(self.last_x, self.last_y, cls)

        # save results
        self.save_results()

        if self.finished_sample:
            self.get_random_sample("finished", 3)


    def patch_on_foreground(self, x, y):
        patch_mask = self.masks["foreground"][y:y+self.p_height, x:x+self.p_width]
        return (patch_mask.sum() / self.p_area) >= self.on_foreground

    def patch_on_annotation(self, cls, x, y):
        patch_mask = self.masks[cls][y:y+self.p_height, x:x+self.p_width]
        return (patch_mask.sum() / self.p_area) >= self.on_annotation

    def get_random_sample(self, phase, sample_count=1):
        for i in range(sample_count):
            x = random.choice(self.x_lefttop)
            y = random.choice(self.y_lefttop)
            patch = self.slide.slide.crop(x, y, self.p_width, self.p_height)
            patch.pngsave("{}/{}/{}_sample/{:06}_{:06}.png".format(self.save_to, self.filestem, phase, x, y))
