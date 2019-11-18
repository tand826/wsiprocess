import openslide


class Slide:

    def __init__(self, path):
        self.slide = openslide.OpenSlide(path)
