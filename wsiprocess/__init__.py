from .slide import Slide as slide
from .patcher import Patcher as patcher
from .annotation import Annotation as annotation
from .rule import Rule as rule
from .converter import Converter as converter

__version__ = "0.7"

_backend = "openslide"


def set_backend(backend):
    """
    Specifies the package used to load and patch images.
    """
    global _backend
    if backend not in ["pyvips", "openslide"]:
        raise ValueError(
            f"Invalid backend {backend}. Options are pyvips and openslide")
    _backend = backend


def get_backend():
    """
    Gets the name of the package used to load and patch images.
    """
    return _backend
