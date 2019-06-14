# wsiprocess
Open Source WSI Processing Library

# memo

```
import wsiprocess as wp
slide = wp.slideread(path)
slide = wp.cvtColor(slide, wp.COLOR_RGB2HSD)
slide = wp.cvtColor(slide, cv2.COLOR_BGR2HSV)
wp.slidewrite("slide.tiff", slide)

mask = wp.maskread(path)
wp.maskwrite("mask.png", mask)
wp.maskwrite("mask_thumb.png", mask.thumb)

new_mask = mask['benign'] - mask['blood_vessel']
wp.maskwrite("new_mask.png", new_mask)

patcher = wp.patchread(path)
patcher = wp.cvtColor(patcher, wp.COLOR_RGB2HSD)
wp.patchwrite("outdir", patcher)
wp.patchwrite("outdir", patcher, mask=mask)
wp.slidewrite("slide.tiff", patcher)
```
