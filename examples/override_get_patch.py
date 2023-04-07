import wsiprocess as wp
slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation()
annotation.make_masks(slide, foreground_fn="otsu")


class AnotherPatcher(wp.patcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_patch(self, x, y, classes):
        print(x, y)


patcher = AnotherPatcher(slide, "evaluation", annotation=annotation, verbose=True)
patcher.get_patch_parallel(classes=["foreground"])
