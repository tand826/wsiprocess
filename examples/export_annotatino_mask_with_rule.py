import wsiprocess as wp
slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("CMU-1_classification.xml")
rule = wp.rule("rule.json")
annotation.make_masks(slide, rule)
annotation.export_thumb_masks("CMU-1/masks")
