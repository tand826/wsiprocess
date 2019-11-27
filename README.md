<img src="images/logo.png" style="max-height: 40px">

Open Source Whole Slide Image(WSI) Processing Library for Deep Learning

# What can wsiprocess do?
<div style="text-align: center"><img src="images/description.png" style="max-width: 50%; margin: 0 auto;"></div>

1. Just make tiles from WSIs without the annotation data.
2. Extract patches from WSIs within the annotated area.
	- Classification: Patch + CSV
	- Object Detection: Patch + CSV
	- Segmentation: Patch + Mask

# Memo
- pip install -e .
	- -> install also as a command line tool

# Installation
1. Install [libvips](https://libvips.github.io/libvips/)
	- Linux
		- `apt install libvips`
	- MacOS
		- `brew install vips`
	- Windows
		- Install tarball from [here](https://github.com/libvips/build-win64)

2. Install wsiprocess
	- `pip install wsiprocess`

# Example

### Basic Usage

```python
import wsiprocess as wp
slide = wp.Slide("xxx.tiff")
annotation = wp.Annotation("xxx.xml")
inclusion = wp.Inclusion("xxx.txt")

annotation.make_masks(slide, inclusion, foreground=True)

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

### From shell

```shell
python wsiprocess.py xxx.tiff xxx.xml xxx.txt
```

# Available WSIs

- From below we tested wsi data.
- The WSIs shown only its file name with green color worked well.
- The WSIs with some descriptions did not work well and colored in red.

### Classification

- Aperio
    - CMU-1-JP2K-33005.svs
    - <div style="color: green">CMU-1-Small-Region.svs</div>
    - <div style="color: green">CMU-1.svs</div>
    - CMU-2.svs
    - CMU-3.svs
    - JP2K-33003-1.svs
    - JP2K-33003-2.svs

- Generic-TIFF
    - <div style="color: red">CMU-1.tiff</div>
    	- Can NOT set magnification.

- Hamamatsu-vms
    - <div style="color: green">CMU-1.zip</div>
    - CMU-2.zip
    - CMU-3.zip
    	+ Could NOT DOWNLOAD from http://openslide.cs.cmu.edu/download/openslide-testdata/Hamamatsu-vms/

- Hamamatsu
    - <div style="color: green">CMU-1.ndpi</div>
    - CMU-2.ndpi
    - CMU-3.ndpi
    - OS-1.ndpi
    - OS-2.ndpi
    - OS-3.ndpi

- Leica
    - <div style="color: green">Leica-1.scn</div>
    - Leica-2.scn
    - Leica-3.scn
    - Leica-Fluorescence-1.scn

- Mirax
    - CMU-1-Exported.zip
    - CMU-1-Saved-1_16.zip
    - CMU-1-Saved-1_2.zip
    - <div style="color: green">CMU-1.zip</div>
    	- Can NOT make the foreground mask.
    - CMU-2.zip
    - CMU-3.zip
    - Mirax2-Fluorescence-1.zip
    - Mirax2-Fluorescence-2.zip
    - Mirax2.2-1.zip
    - Mirax2.2-2.zip
    - Mirax2.2-3.zip
    - Mirax2.2-4-BMP.zip
    - Mirax2.2-4-PNG.zip

- Olympus
    - OS-1.zip
    - OS-2.zip
    - OS-3.zip

- Trestle
    - <div style="color: red">CMU-1.zip</div>
    	- ASAP can NOT show the image properly, and cannot annotate.
    - CMU-2.zip
    - CMU-3.zip

- Ventana
    - OS-1.bif
    - OS-2.bif

- <div style="color: red">Zeiss</div>
    - <div style="color: red">Zeiss-1-Merged.zvi</div>
    	- Can NOT load slide
    - <div style="color: red">Zeiss-1-Stacked.zvi</div>
    	- Can NOT load slide
    - <div style="color: red">Zeiss-2-Merged.zvi</div>
    	- Can NOT load slide
    - <div style="color: red">Zeiss-2-Stacked.zvi</div>
    	- Can NOT load slide
    - <div style="color: red">Zeiss-3-Mosaic.zvi</div>
    	- Can NOT load slide
    - <div style="color: red">Zeiss-4-Mosaic.zvi</div>
    	- Can NOT load slide


# Test

1. Download sample WSI
```
curl -O -C - http://openslide.cs.cmu.edu/download/openslide-testdata/CMU-1.ndpi
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
