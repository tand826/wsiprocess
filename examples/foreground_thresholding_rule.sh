# foreground area is normally calculated with Otsu's threshold.
# if --minmax is set, in the case below, foreground area is defined
# with the area which has from 10 to 230 in the scale of 0-255.
wsiprocess evaluation CMU-1.ndpi --minmax 10-230
