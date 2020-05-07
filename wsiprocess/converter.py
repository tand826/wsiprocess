# -*- coding: utf-8 -*-
"""Convert wsiprocess style annotation data to COCO or VOC style.
"""

class Converter:
    """Converter Class
    Args:

    Attributes:


    """
    def __init__(self, root, save_to, ratio_arg):
        self.params = {"root": root, "save_to": save_to, "ratio_arg": ratio_arg}

    def to_coco(self):
        from .converters import wsiprocess_to_coco
        converter = wsiprocess_to_coco.ToCOCOConverter(self.params)
        converter.convert()

    def to_voc(self):
        from .converters import wsiprocess_to_voc
        converter = wsiprocess_to_voc.ToVOCConverter(self.params)
        converter.convert()
