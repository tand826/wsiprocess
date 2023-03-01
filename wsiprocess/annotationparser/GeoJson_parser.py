import json

from .parser_utils import BaseParser


class GeoJsonAnnotation(BaseParser):
    """Parser for GeoJson styled Annotation.

    Example:
        >>> with open("xxx.geojson", "r") as f:
        >>>     annotations = geojson.load(f)
        >>> print(annotations)
        >>> {
        >>>     "type": "FeatureCollection",
        >>>     "features": [
        >>>         {
        >>>             "type": "Feature",
        >>>             "properties": {
        >>>                 "class": 0
        >>>             },
        >>>             "geometry": {
        >>>                 "type": "Polygon",
        >>>                 "coordinates": [
        >>>                     [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
        >>>                 ]
        >>>             }
        >>>         }
        >>>     ]
        >>> }
    """

    def __init__(self, path):
        """
        Args:
            path (str): Path to the annotation file.
        """
        super().__init__(path)
        self.read_annotation()

    def read_annotation(self):
        """Read the annotation file."""

        with open(self.path, "r") as f:
            annotations = json.load(f)
        assert annotations["type"] == "FeatureCollection"

        classes = set()
        for annotation in annotations["features"]:
            class_ = annotation["properties"]["class"]
            classes.add(class_)
            self.mask_coords[class_].append(annotation["geometry"]["coordinates"])

        self.classes = list(classes)
