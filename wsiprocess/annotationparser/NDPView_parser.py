# -*- coding: utf-8 -*-
from typing import List
from dataclasses import dataclass
import math

from lxml import etree

from .parser_utils import BaseParser


@dataclass
class Coord:
    x: float
    y: float


@dataclass
class MPP:
    x: float
    y: float
    r: float

    def meter2px(self, meter: float, axis: str, coordformat: str) -> float:
        """Convert meter to pixel.

        Args:
            meter (float): Length in meter.
            axis (str): mpp to use along this axis.

        Returns:
            int: Length in pixel.
        """

        if coordformat == "nanometers":
            unit = 1000
        elif coordformat == "micrometers":
            unit = 1
        elif coordformat == "millimeters":
            unit = 0.001
        else:
            raise ValueError(f"Invalid coordformat: {coordformat}")
        return int(meter / unit / getattr(self, axis))


class Annotation:
    """Annotations of NDP View.

    Args:
        element (etree.Element): Element of the annotation.
        origin (Coord): Origin of the slide.
        mpp (MPP): MPP of the slide.

    Attributes:
        element (etree.Element): Element of the annotation.
        title (str): Title of the annotation. Used as the class.
        coordformat (str): Coordinate format.
        type (str): Type of the annotation. One of AnnotateCircle, AnnotateFreehandLine, AnnotateRectangle,
            AnnotatePin, AnnotateFreehand
    """

    def __init__(self, element: etree.Element, origin: Coord, mpp: MPP):
        self.element = element
        self.origin = origin
        self.mpp = mpp

        self.coordformat = element.find("coordformat").text
        self.type = element.find("annotation").attrib["displayname"]
        assert self.type in [
            "AnnotateCircle",
            "AnnotateFreehandLine",
            "AnnotateRectangle",
            "AnnotatePin",
            "AnnotateFreehand"], f"Annotation type {self.type} is not supported."

        self._coords = self.get_coords()

    @property
    def title(self):
        title = self.element.find("title").text
        return title if title else "NOTITLE"

    @property
    def coords(self):
        return self._coords

    def get_coords(self):
        if self.type == "AnnotateCircle":
            return self.get_circle_coords()
        elif self.type == "AnnotatePin":
            return self.get_pin_coords()
        else:
            return self.get_polygon_coords()

    def get_circle_coords(self) -> List[int]:
        """Get the coordinates of the circle annotation."""
        center = Coord(
            x=self.origin.x + self.mpp.meter2px(
                int(self.element.find("annotation/x").text), "x",
                self.coordformat),
            y=self.origin.y + self.mpp.meter2px(
                int(self.element.find("annotation/y").text), "y",
                self.coordformat)
        )
        radius = self.mpp.meter2px(
            int(self.element.find("annotation/radius").text), "r",
            self.coordformat)

        coords = []
        n = 100
        for i in range(0, n):
            coords.append([
                int(center.x + radius * math.cos(2*math.pi/n*i)),
                int(center.y + radius * math.sin(2*math.pi/n*i))
            ])
        return coords

    def get_pin_coords(self) -> List[int]:
        """Get the coordinate of Pin annotation"""
        coord = Coord(
            x=self.mpp.meter2px(
                int(self.element.find("annotation/x").text), "x",
                self.coordformat),
            y=self.mpp.meter2px(
                int(self.element.find("annotation/y").text), "y",
                self.coordformat)
        )
        return [
            [self.origin.x + coord.x, self.origin.y + coord.y]
        ]

    def get_polygon_coords(self) -> List[int]:
        """Get coordinates of rectangle, freehand, freehandline polygons.
        The coordinates are assumed to be closed.
        """
        coords = []
        for point in self.element.findall("annotation/pointlist/point"):
            x = self.mpp.meter2px(
                int(point.find("x").text), "x", self.coordformat)
            y = self.mpp.meter2px(
                int(point.find("y").text), "y", self.coordformat)
            coords.append([self.origin.x + x, self.origin.y + y])
        return coords


def get_origin(slide, mpp: MPP, coordformat: str):
    center = Coord(x=slide.width//2, y=slide.height//2)
    offset = Coord(
        x=int(getattr(slide, "hamamatsu.XOffsetFromSlideCentre")),
        y=int(getattr(slide, "hamamatsu.YOffsetFromSlideCentre"))
    )
    return Coord(
        x=center.x - mpp.meter2px(offset.x, "x", coordformat),
        y=center.y - mpp.meter2px(offset.y, "y", coordformat)
    )


def get_mpp(slide):
    mpp_x = float(getattr(slide, "openslide.mpp-x"))
    mpp_y = float(getattr(slide, "openslide.mpp-y"))
    mpp_r = (float(mpp_x) + float(mpp_y)) / 2
    return MPP(x=mpp_x, y=mpp_y, r=mpp_r)


class NDPViewAnnotation(BaseParser):
    """Annotation Parser for NDP View.
    https://www.hamamatsu.com/jp/ja/product/life-science-and-medical-systems/digital-slide-scanner/U12388-01.html

    Args:
        path (str): Path to the annotation file.
        slide (wsiprocess.Slide): Slide object.

    Attributes:
        path (str): Path to the annotation file.
        annotations (list): List of etree Elements.
        annotation_groups (list): List of etree Elements.
        classes (list): List of classes defined with ASAP.
        mask_coords (dict): Coordinates of the masks.
    """

    def __init__(self, path, slide):
        super().__init__(path)
        self.slide = slide
        self.tree = etree.parse(self.path)
        mpp = get_mpp(slide)
        origin = get_origin(
            slide, mpp, coordformat=self.tree.find("//coordformat").text)
        self.read_annotation(origin, mpp)

    def read_annotation(self, origin, mpp):
        for element in self.tree.xpath("/annotations/ndpviewstate"):
            annotation = Annotation(element, origin, mpp)
            self.classes.append(annotation.title)
            self.mask_coords[annotation.title].append(annotation.coords)
