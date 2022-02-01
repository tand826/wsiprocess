<div align="center">
<img src="https://raw.githubusercontent.com/tand826/wsiprocess/master/images/wsiprocess.svg" style="width: 50%">

![Documentation](https://readthedocs.org/projects/wsiprocess/badge/?version=latest)
![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4629396.svg)
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

See [Wiki](https://github.com/tand826/wsiprocess/wiki) for 
1. [available applications for annotation](https://github.com/tand826/wsiprocess/wiki/annotation_applications), 
2. [speed comparison](https://github.com/tand826/wsiprocess/wiki/speed_comparison) between patched images and loading from raw WSIs,
3. [how to use the other annotatiion files](https://github.com/tand826/wsiprocess/wiki/How-to-use-custom-annotation-parser).

# Installation

### pip User

1. Install [openslide](https://openslide.org/) or [libvips](https://libvips.github.io/libvips/). See [wiki] for installation hints.

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

- [Documentation](https://tand826.github.io/wsiprocess/)

# Example

### As a python module

- see [examples](https://github.com/tand826/wsiprocess/tree/master/examples)
- see [wsiprocess/cli.py](https://github.com/tand826/wsiprocess/blob/master/wsiprocess/cli.py) to check the detailed flow.

### As a command line tool

- see [examples](https://github.com/tand826/wsiprocess/tree/master/examples).

# Available annotation tools

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
@software{takumi_ando_2021_4629396,
  author       = {Takumi Ando},
  title        = {tand826/wsiprocess: version 0.8},
  month        = mar,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v0.8},
  doi          = {10.5281/zenodo.4629396},
  url          = {https://doi.org/10.5281/zenodo.4629396}
}
```
