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

# Example

#### Basic usage

```python
import wsiprocess as wp
slide = wp.slide(path_slide)
annotation = wp.annotation(path_annotation)
inclusion = wp.inclusion(path_inclusion)

annotation.to_mask(slide, inclusion)

patcher = wp.patcher(slide, method, patch_width, patch_height, overlap_width,
	 			     overlap_height, annotation, on_foreground, on_annotation,
	 			     start_sample, finished_sample, extract_patches, output_dir)
patcher.get_patch_parallel(cls, 12)
```

#### Export annotaton xml as mask image

```python
annotation = wp.annotation(path)
annotation.export_mask(output_dir)
```

