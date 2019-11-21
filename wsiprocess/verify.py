from pathlib import Path


class Verify:

    def __init__(self, save_to, classes, filestem, method, start_sample, finished_sample, extract_patches):
        self.save_to = save_to
        self.classes = classes
        self.filestem = filestem
        self.method = method
        self.start_sample = start_sample
        self.finished_sample = finished_sample
        self.extract_patches = extract_patches

    def verify_dirs(self):
        base_dir = Path(self.save_to)/self.filestem
        self._verify_dir(base_dir)
        if self.method == "segmentation":
            self._verify_dir(base_dir/"masks")
        if self.start_sample:
            self._verify_dir(base_dir/"start_sample")
        if self.finished_sample:
            self._verify_dir(base_dir/"finished_sample")
        if self.extract_patches:
            self._verify_dir(base_dir/"patches")
        for cls in self.classes:
            self._verify_dir(base_dir/"patches"/cls)

    @staticmethod
    def _verify_dir(path):
        if not path.exists():
            path.mkdir(parents=True)

    def verify_magnification(self, slide, magnification):
        basemsg = "Magnification for this slide has to be smaller than"
        msg = "{} {}".format(basemsg, slide.slide.magnification)
        assert slide.slide.magnification < magnification, msg
