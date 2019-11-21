import wsiprocess as wp
from pathlib import Path


slide = wp.Slide(f"{Path().home()}/datasets/leiomyoma/#S05H17-162112 - 2019-02-16 09.30.09.ndpi")
# annotation = wp.Annotation(f"{Path().home()}/datasets/leiomyoma/#S05H17-162112 - 2019-02-16 09.30.09.xml")
# inclusion = wp.Inclusion(f"{Path().home()}/datasets/leiomyoma/inc.txt")
# annotation.make_masks(slide, foreground=True)
# annotation.export_thumb_mask(cls="foreground", save_to=".")
# annotation.export_thumb_masks(".")

patcher = wp.Patcher(slide, "none", start_sample=False, finished_sample=False, on_foreground=False, on_annotation=False)
# patcher = wp.Patcher(slide, "none", annotation, start_sample=False, finished_sample=False, extract_patches=False)
patcher.get_patch_parallel()
