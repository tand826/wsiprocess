# Extract patches for classification task on condition that
# each patch has to be on the annotated area at least 50%,
# and on the foreground area at least 80%. 
# If the patch width == height == 256, 256x256x0.5 = 32768 pixels of the patch are on the annotated area.

wsiprocess classification CMU-1.ndpi CMU-1_classification.xml --on_annotation 0.5 -on_foreground 0.8
