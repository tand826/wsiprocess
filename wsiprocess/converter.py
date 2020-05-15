# -*- coding: utf-8 -*-
"""Convert wsiprocess style annotation data to COCO or VOC style.
"""
from .converters import (
    wsiprocess_to_coco,
    wsiprocess_to_voc,
    wsiprocess_to_yolo
)


class Converter:
    """Converter Class
    Args:

    Attributes:


    """
    def __init__(self, root, save_to, ratio_arg):
        self.params = {"root": root, "save_to": save_to, "ratio_arg": ratio_arg}

    def to_coco(self):
        converter = wsiprocess_to_coco.ToCOCOConverter(self.params)
        converter.convert()

    def to_voc(self):
        converter = wsiprocess_to_voc.ToVOCConverter(self.params)
        converter.convert()

    def to_yolo(self):
        converter = wsiprocess_to_yolo.ToYOLOConverter(self.params)
        converter.convert()
