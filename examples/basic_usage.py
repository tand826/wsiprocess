import wsiprocess as wp
slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("CMU-1_classification.xml")
rule = wp.rule("rule.json")

annotation.make_masks(slide, rule, foreground_fn="otsu")

patcher = wp.patcher(slide, "classification", annotation)
patcher.get_patch_parallel(["benign", "malignant"])
