from slide import Slide
from mask import Mask
from annotation import Annotation
from classes import Classes


def slideread(path):
    return Slide(path)


def slidewrite(save_as, slide):
    pass


def maskread(path):
    return Mask(path)


def maskwrite(save_as, mask):
    pass


def patchread(path):
    pass


def patchwrite(save_as, patch):
    pass


def annotationread(path):
    return Annotation(path)


def annotationwrite(save_as, annotation):
    pass


def classesread(path):
    return Classes(path)


def classeswrite(save_as, classes):
    pass


if __name__ == '__main__':
    # Test codes
    from arguments import Args
