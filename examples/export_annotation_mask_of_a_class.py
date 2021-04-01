import wsiprocess as wp
slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("CMU-1_classification.xml")
annotation.make_masks(slide)
annotation.export_mask("CMU-1/masks", "benign")
