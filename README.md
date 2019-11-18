# wsiprocess
Open Source WSI Processing Library

# Flow
0. Options(for all)
	- crop background?
	- all on annotation area?
	- patch size
	- overlap size
	- start sample
	- finished sample
	- extract patches?
	- magnification
	- include exclude classes
1. Input
	- WSI(xxx.csv)
	- Annotation(xxx.xml)
    	+ no
    		+ Targets all the area.
    	+ yes
    		+ Targets in the annotated area.
2. Task
	- N/A(in case of no annotations)
		- xxx.csv
			- (left, top, right, bottom) per patch
		- xxx/left_top_right_bottom.png
	- classification
		- xxx.csv
			- (left, top, right, bottom, class) per patch
		- xxx/left_top_right_bottom.png
		- xxx.cls
			- (0: classname1, 1: classname2,...) per patch
	- object detection
		- xxx.csv
			- (left, top, right, bottom), (left, top, right, bottom (of annotation), class),... per patch
		- xxx/left_top_right_bottom.png
		- xxx.cls
		- option
			- extract one crop per one annotation?
			- extract patch without annotation?
	- segmentation
		- xxx.csv
			- (left, top, right, bottom), ((coordx1, coordy1), (coordx2, coordy2),..., class), ... per patch
		- xxx/left_top_right_bottom.png
		- xxx.cls

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
