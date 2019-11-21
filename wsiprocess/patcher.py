import random
from joblib import Parallel, delayed
from itertools import product
import csv


class Patcher:

    def __init__(self, slide, method, annotation=False, output_dir=".", patch_width=256, patch_height=256,
                 overlap_width=1, overlap_height=1, on_foreground=1., on_annotation=1.,
                 start_sample=True, finished_sample=True, extract_patches=True):
        self.slide = slide
        self.filename = slide.filename
        self.p_width = patch_width
        self.p_height = patch_height
        self.p_area = self.p_width * self.p_height
        self.o_width = overlap_width
        self.o_height = overlap_height
        self.x_lefttop = [i for i in range(0, self.wsi_width, self.p_width - self.o_width)][:-1]
        self.y_lefttop = [i for i in range(0, self.wsi_height, self.p_height - self.o_height)][:-1]
        self.iterator = product(self.x_lefttop, self.y_lefttop)
        self.last_x = self.slide.width - self.p_width
        self.last_y = self.slide.height - self.p_height

        self.annot = annotation
        self.clses = annotation.clses

        self.output_dir = output_dir

        self.on_foreground = on_foreground
        self.on_annotation = on_annotation
        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.extract_patches = extract_patches

        self.result = []

    def get_patch(self, cls, x, y):
        patch = self.slide.crop(x, y, self.p_width, self.p_height)
        if self.on_foreground:
            if not self.is_on_foreground(x, y):
                return
        if self.on_annotation:
            if not self.is_on_annotation(cls, x, y):
                return
        self.result.append([x, y, self.p_width, self.p_height, cls])
        if self.extract_patches:
            patch.pngsave("{}/{}/patches/{}/{:06}_{:06}.png".format(self.output_dir, self.filename, cls, x, y))

    def get_parallel(self, cls, cores=-1):
        parallel = Parallel(n_jobs=cores, backend="threading")

        # from the left top to just before the right bottom.
        parallel([delayed(self.get_patch)(cls, x, y) for x, y in self.iterator])

        # the bottom edge.
        parallel([delayed(self.get_patch)(cls, x, self.last_y) for x in self.x_lefttop])

        # the right edge
        parallel([delayed(self.get_patch)(cls, self.last_x, y) for y in self.y_lefttop])

        # right bottom patch
        self.get_patch(cls, self.last_x, self.last_y)

        # save results
        with open("{}/{}/{}.csv".format(self.output_dir, self.filename, self.filename), "w") as f:
            writer = csv.writer(f)
            writer.rows(self.result)

    def is_on_foreground(self, x, y):
        patch_mask = self.annotation.masks["foreground"][x:x+self.p_width, y:y+self.p_height]
        return (patch_mask.sum() / self.p_area) > self.on_foreground

    def is_on_annotation(self, cls, x, y):
        patch_mask = self.annotation.masks[cls][x:x+self.p_width, y:y+self.p_height]
        return (patch_mask.sum() / self.p_area) > self.on_annotation

    def get_random_sample(self, phase, sample_count=1):
        for i in range(sample_count):
            x = random.choice(self.x_lefttop)
            y = random.choice(self.y_lefttop)
            patch = self.slide.crop(x, y, self.p_width, self.p_height)
            patch.pngsave("{}/{}/{}_sample/{:06}_{:06}.png".format(self.output_dir, self.filename, phase, x, y))


class Classification(Patcher):

    def __init__(self, slide, patch_width, patch_height, overlap_width,
                 overlap_height, output_dir):
        super().__init__(slide, patch_width, patch_height, overlap_width,
                         overlap_height, output_dir)
        pass


class Detection(Patcher):

    def __init__(self, slide, patch_width, patch_height, overlap_width,
                 overlap_height, output_dir):
        super().__init__(slide, patch_width, patch_height, overlap_width,
                         overlap_height, output_dir)
        pass


class Segmentation(Patcher):

    def __init__(self, slide, patch_width, patch_height, overlap_width,
                 overlap_height, output_dir):
        super().__init__(slide, patch_width, patch_height, overlap_width,
                         overlap_height, output_dir)
        pass