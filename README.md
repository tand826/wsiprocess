# wsiprocess
Open Source Whole Slide Image(WSI) Processing Library for Deep Learning

# What can wsiprocess do?
1. Just make tiles from WSIs without the annotation data.
2. Extract patches from WSIs within the annotated area.
	- Classification: Patch + CSV
	- Object Detection: Patch + CSV
	- Segmentation: Patch + Mask

# Installation
1. Install [libvips](https://libvips.github.io/libvips/)
	- MacOS
		- `brew install vips`
	- Linux
		- `apt install libvips`
	- Windows
		- Install tarball from [here](https://github.com/libvips/build-win64)

2. [For magnification utility] Install [openslide](https://openslide.org/)
	- MacOS
		- `brew install openslide`
	- Linux
		- `apt install libvips  # automatically instaled with libvips`
	- Windows
		- Download the precompiled binary from [here](https://openslide.org/download/#windows-binaries)

3. Install wsiprocess
	- `pip install wsiprocess`

# Example

### Basic Usage

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
inclusion = wp.Inclusion("xxx.txt")

annotation.make_masks(slide, inclusion)

patcher = wp.Patcher(slide, "classification", annotation)
patcher.get_patch_parallel("benign")
```

### Export annotaton xml of one class as mask image

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
annotation.make_masks(slide)
annotation.export_mask("xxx/masks", "benign")
```

### Export annotation xml with inclusion definition as mask images, and save their thumbs

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
inclusion = wp.Inclusion("xxx.txt")
annotation.make_masks(slide, inclusion)
annotation.export_thumb_masks("xxx/masks")
```

# Test

1. Download sample WSI
```
curl -O -C - http://openslide.cs.cmu.edu/download/openslide-testdata/Hamamatsu/CMU-1.ndpi
```

2. Make random annotation
- Install ASAP ( Linux / Windows )
	- https://github.com/computationalpathologygroup/ASAP/releases
- Open CMU-1.ndpi and make some random annotation.
	- Save the annotation xml as "CMU-1.xml".

3. Run test.py
```
python test.py
```


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
