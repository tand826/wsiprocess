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
	- none
		+ w/ annotation
			+ xxx.csv
				+ (left, top, right, bottom) per patch
			+ xxx/left_top_right_bottom.png
		+ w/o annotation
			+ xxx.csv
				+ (left, top, right, bottom) per patch
			+ xxx/left_top_right_bottom.png
	- classification
			+ xxx.csv
				+ (left, top, right, bottom, class) per patch
			+ xxx/left_top_right_bottom.png
			+ xxx.cls
				+ (0: classname1, 1: classname2,...) per patch
	- object detection
			+ xxx.csv
				+ (left, top, right, bottom), (left, top, right, bottom (of annotation), class),... per patch
			+ xxx/left_top_right_bottom.png
			+ xxx.cls
			+ option
				+ extract one crop per one annotation?
				+ extract patch without annotation?
	- segmentation
			+ xxx.csv
				+ (left, top, right, bottom), ((coordx1, coordy1), (coordx2, coordy2),..., class), ... per patch
			+ xxx/left_top_right_bottom.png
			+ xxx.cls

# Example

### Basic usage

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
annotation.make_masks(slide)
patcher = wp.Patcher(slide, "classification", annotation)
patcher.get_patch_parallel(cls="benign", cores=12)
```

### Export annotaton xml of one class as mask image

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
annotation.make_masks(slide)
annotation.export_mask("xxx/masks", "benign")
```

### Export annotation xml with inclusion relationship as mask images, and save their thumbs

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
inclusion = wp.Inclusion("xxx.txt")
annotation.make_masks(slide, inclusion)
annotation.export_thumb_masks("xxx/thumbs")
```

