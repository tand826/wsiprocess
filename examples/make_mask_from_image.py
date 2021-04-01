import wsiprocess as wp
import cv2


slide = wp.slide("CMU-1.ndpi")
annotation = wp.annotation("", is_image=True)
target_classes = ["benign", "malignant"]
annotation.add_class(target_classes)

benign_mask = cv2.imread("benign_mask.png", 0) * 255
malignant_mask = cv2.imread("malignant_mask.png", 0) * 255

# Make sure your mask data includes only 0 as background or 255 as foreground
annotation.from_image(benign_mask, "benign")
annotation.from_image(malignant_mask, "malignant")

patcher = wp.patcher(slide, "classification", annotation=annotation)
patcher.get_patch_parallel(target_classes)
