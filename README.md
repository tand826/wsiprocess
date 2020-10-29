<div align="center">
<img src="https://raw.githubusercontent.com/tand826/wsiprocess/master/images/wsiprocess.svg" style="width: 50%">

![Documentation](https://readthedocs.org/projects/wsiprocess/badge/?version=latest)
![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.4065072.svg)
![Downloads](https://pepy.tech/badge/wsiprocess)
![PyPI](https://img.shields.io/pypi/v/wsiprocess)
![conda](https://anaconda.org/tand826/wsiprocess/badges/version.svg)
</div>

Convert Helper for Histopathological / Cytopathological Machine Learning Tasks

# Main Flow

<div align="center">
<img src="https://raw.githubusercontent.com/tand826/wsiprocess/master/images/description.png" style="max-width: 80%">
</div>

1. Scan some WSIs.
2. Make some annotations with WSI annotation tools. ([ASAP](https://github.com/computationalpathologygroup/ASAP/releases) and [SlideRunner v.1.31.0](https://github.com/DeepPathology/SlideRunner), [QuPath v0.2.3](https://github.com/qupath/qupath) are now available. See [wiki](https://github.com/tand826/wsiprocess/wiki) for details.)
3. Then wsiprocess helps converting WSI + Annotation data into patches and easy-to-use annotation data.

[WSIPatcher](https://github.com/tand826/WSIPatcher) will give you GUI.



# Installation

### pip User

1. Install [libvips](https://libvips.github.io/libvips/)

  - Linux

    1. Install the following packages with your package manager.

        ```
        build-essential pkg-config libglib2.0-dev libexpat1-dev libtiff5-dev libjpeg-turbo8-dev libgsf-1-dev openslide-tools libpng-dev
        ```

    2. Download libvips v8.10.1 from [here](https://github.com/libvips/libvips/releases).

    3. Install libvips
        ```
        tar xvfz vips-8.10.1.tar.gz
        cd vips-8.10.1 && ./configure && make -j && sudo make install
        ```

   - MacOS - `brew install vips`
   - Windows - Install tarball from [here](https://github.com/libvips/build-win64)

2. Install wsiprocess

   ```
   pip install wsiprocess
   ```

### Anaconda User

```
# Only for python 3.6 or higher
conda install -c tand826 wsiprocess
```

# Documentation

- [Documentation](https://wsiprocess.readthedocs.io)

# Example

### As a python module

- see [wsiprocess/cli.py](https://github.com/tand826/wsiprocess/blob/master/wsiprocess/cli.py) to check the flow.

#### Basic Usage

```python
import wsiprocess as wp
slide = wp.slide("xxx.tiff")
annotation = wp.annotation("xxx.xml")
rule = wp.rule("xxx.json")

annotation.make_masks(slide, rule, foreground=True)

patcher = wp.patcher(slide, "classification", annotation)
patcher.get_patch_parallel(["benign", "malignant"])
```

#### Export annotaton xml of one class as mask image

```python
import wsiprocess as wp
slide = wp.slide("xxx.tiff")
annotation = wp.annotation("xxx.xml")
annotation.make_masks(slide)
annotation.export_mask("xxx/masks", "benign")
```

#### Export annotation xml with inclusion definition as mask images, and save their thumbs

```python
import wsiprocess as wp
slide = wp.slide("xxx.tiff")
annotation = wp.annotation("xxx.xml")
rule = wp.rule("xxx.json")
annotation.make_masks(slide, rule)
annotation.export_thumb_masks("xxx/masks")
```

#### Make foreground mask with custom function and extract only the patches of benign for classification task.

```python
import numpy as np
def example_function(thumb_gray):
    assert len(thumb_gray.shape) == 2
    assert isinstance(thumb_gray, np.ndarray)
    thresh = 100
    thumb_gray[thumb_gray > thresh] = 1
    thumb_gray[thumb_gray <= thresh] = 0
    assert np.sum((thumb_gray == 0) | (thumb_gray == 1)) == len(thumb_gray)
    return thumb_gray

import wsiprocess as wp
slide = wp.slide("xxx.tiff")
annotation = wp.annotation("xxx.xml")
annotation.make_masks(slide, foreground=example_function)
patcher = wp.patcher(slide, "classification", annotation)
patcher.get_patch_parallel(["benign"])
```

#### Load mask data from image, and extract patches.

```python
import wsiprocess as wp
import cv2
slide = wp.slide("xxx.tiff")
annotation = wp.annotation("", is_image=True)
target_classes = ["benign", "malignant"]
annotation.add_class(target_classes)
benign_mask = cv2.imread("benign_mask.png", 0) * 255
malignant_mask = cv2.imread("malignant_mask.png", 0) * 255
# Make sure your mask data includes only 0 as background or 255 as foreground
annotation.from_image(benign_mask, "benign")
annotation.from_image(malignant_mask, "malignant")
rule = wp.rule("xxx.json")
patcher = wp.patcher(slide, "classification", annotation=annotation)
patcher.get_patch_parallel(target_classes)
```

### As a command line tool (recommended)

#### basic flow

```bash
wsiprocess [your method] xxx.tiff xxx.xml
```

#### Extract patches of width = height = 256 pixels for classification with thumbnails of the annotation results.

```bash
wsiprocess classification xxx.tiff xxx.xml --export_thumbs
```

#### Extract patches for classification task on condition that each patch has to be on the annotated area at least 50%, and on the foreground area at least 80%. (If the patch width = height = 256, 256x256x0.5 = 32768 pixels of the patch are on the annotated area.)

```bash
wsiprocess classification xxx.tiff xxx.xml --on_annotation 0.5 -on_foreground 0.8
```

#### Extract patches and coco/voc/yolo styled detection annotation data on condition that each patch has to be on the annotated area at least 1% and on the foreground area at least 1%.

```bash
wsiprocess detection xxx.tiff xxx.xml --on_annotation 0.01 -on_foreground 0.01 --coco_style --voc_style --yolo_style
```

#### Extract patches and masks for segmentation task.

```bash
wsiprocess segmentation xxx.tiff xxx.xml
```

#### Extract patches with mask of foreground area for evaluation or inference of models. The mask has pixels with 1 as foreground which are originally from 10 to 230 in the scale of 0-255, and pixels with 0 as background which are originally from 0 to 10 and from 230 to 255.

```bash
wsiprocess none xxx.tif --minmax 10-230
```

#### Just to check the thumbnails to see where the annotations should be.

```bash
wsiprocess classification xxx.tif --no_patches --export_thumbs
```

#### Crop bounding boxes after extracting patches

```
wsiprocess detection xxx.tif xxx.xml --crop_bbox
```

#### Translate dot annotations to bounding boxes and set their width to 100 pixels

```
wsiprocess classification xxx.tif xxx.xml --dot_bbox_width 100
```


- Need recommendation for choice of arguments? Type `wsiprocess -h` or `wsiprocess [your method] -h` to see options.

### As a docker command line tool (not working on)

```bash
# build the image
docker build . -t wsiprocess_image

# run the container
docker run --name wsiprocess_container -v [your files directory]:/data -it -d wsiprocess_image [commands] etc.
```

### Convert to VOC / COCO / YOLO style format


```bash
# If already extracted patches...
# to COCO format
python wsiprocess/converters/wsiprocess_to_coco.py [directory containing results.json] -s [directory to save to] -r [ratio of train, val and test]

# to VOC foramt
python wsiprocess/converters/wsiprocess_to_voc.py [directory containing results.json] -s [directory to save to] -r [ratio of train, val and test]

# to YOLO format
python wsiprocess/converters/wsiprocess_to_yolo.py [directory containing results.json] -s [directory to save to] -r [ratio of train, val and test]

```

```bash
# If not extracted patches yet...
# convert to VOC and COCO and YOLO
wsiprocess xxx.tiff detection xxx.xml -vo -co -yo
```

# Available annotations

- [ASAP](https://github.com/computationalpathologygroup/ASAP/)
- [SlideRunner version 1.31.0](https://github.com/DeepPathology/SlideRunner)
- [QuPath v0.2.3](https://github.com/qupath/qupath)

details: [wiki](https://github.com/tand826/wsiprocess/wiki)

# Available WSIs

<details>
    <summary>Test ongoing</summary>
    <div>

- From below we tested wsi data.

  - :smile: => worked well.
  - :umbrella: => did not work well.
  - otherwise => did not check

- Aperio

  - CMU-1-JP2K-33005.svs
  - :smile: CMU-1-Small-Region.svs
  - :smile: CMU-1.svs
  - CMU-2.svs
  - CMU-3.svs
  - JP2K-33003-1.svs
  - JP2K-33003-2.svs

- Generic-TIFF

  - :umbrella:CMU-1.tiff
    - Can not set magnification.

- Hamamatsu-vms

  - :smile:CMU-1.zip
  - CMU-2.zip
  - CMU-3.zip
    - Could not DOWNLOAD from http://openslide.cs.cmu.edu/download/openslide-testdata/Hamamatsu-vms/

- Hamamatsu

  - :smile:CMU-1.ndpi
  - CMU-2.ndpi
  - CMU-3.ndpi
  - OS-1.ndpi
  - OS-2.ndpi
  - OS-3.ndpi

- Leica

  - :smile:Leica-1.scn
  - Leica-2.scn
  - Leica-3.scn
  - Leica-Fluorescence-1.scn

- Mirax

  - CMU-1-Exported.zip
  - CMU-1-Saved-1_16.zip
  - CMU-1-Saved-1_2.zip
  - :umbrella:CMU-1.zip
    - Can not make the foreground mask.
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

  - :umbrella:CMU-1.zip
    - ASAP can not show the image properly, and it's hard to annotate.
  - CMU-2.zip
  - CMU-3.zip

- Ventana

  - OS-1.bif
  - OS-2.bif

- :umbrella:Zeiss : Can not load slide - :umbrella:Zeiss-1-Merged.zvi - :umbrella:Zeiss-1-Stacked.zvi - :umbrella:Zeiss-2-Merged.zvi - :umbrella:Zeiss-2-Stacked.zvi - :umbrella:Zeiss-3-Mosaic.zvi - :umbrella:Zeiss-4-Mosaic.zvi
</div>
</details>

# Test

### Download sample WSI

```
curl -O -C - https://data.cytomine.coop/open/openslide/hamamatsu-ndpi/CMU-1.ndpi
```

### Make random annotation

- Install ASAP ( Linux / Windows ) - https://github.com/computationalpathologygroup/ASAP/releases
- Open CMU-1.ndpi and make some random annotation. - Save the annotation xml as "CMU-1.xml".

### Run test.py

```
cd tests
pytest tests.py
```

# Citation

```
@software{takumi_ando_2020_4065072,
  author       = {Takumi Ando},
  title        = {tand826/wsiprocess: version 0.6},
  month        = oct,
  year         = 2020,
  publisher    = {Zenodo},
  version      = {v0.6},
  doi          = {10.5281/zenodo.4065072},
  url          = {https://doi.org/10.5281/zenodo.4065072}
}
```
