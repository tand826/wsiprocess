from slide import Slide
from patcher import Patcher
from mask import Mask
from annotation import Annotation
from inclusion import Inclusion


def slideread(path):
    """[summary]

    [description]

    Arguments:
        path {pathlib.PosixPath} -- Path to the wsi data.

    Returns:
        [slide.Slide] -- Slide object with the wsi info.
    """
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


def inclusionread(path):
    return Inclusion(path)


def inclusionwrite(save_as, inclusion):
    pass


if __name__ == '__main__':
    # Test codes
    from arguments import Args

    def run():
        args = Args()
        slide = Slide(args.wsi)
        wsi_width = slide.wsi_width
        wsi_height = slide.wsi_height

        if args.method == "none":

            if args.annotation:
                annot = Annotation(args.annotation)

                if args.inclusion_relationship:
                    inclusion = Inclusion(args.inclusion_relationship)
                    annot.to_mask(wsi_height, wsi_width, inclusion)
                else:
                    annot.to_mask(wsi_height, wsi_width)
                patcher = Patcher(slide, args.method, args.patch_width,
                                  args.patch_height, args.overlap_width,
                                  args.overlap_height, annot,
                                  args.on_foreground, args.on_annotation,
                                  args.start_sample, args.finished_sample,
                                  args.extract_patches, args.output_dir)
                for cls in annot.clses:
                    patcher.get_patch_parallel(cls, 12)

            else:
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               args.only_foreground,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)

        elif args.method == "classification":

            if args.annotation:
                annot = Annotation(args.annotation)

                if args.inclusion_relationship:
                    inclusion = Inclusion(args.inclusion_relationship)
                    annot.to_mask(wsi_height, wsi_width, inclusion)
                else:
                    annot.to_mask(wsi_height, wsi_width)
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               annot, args.patch_without_annotation,
                               args.only_foreground, args.patch_on_annotated,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)
            else:
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               args.only_foreground,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)

        elif args.method == "detection":

            if args.annotation:
                annot = Annotation(args.annotation)

                if args.inclusion_relationship:
                    inclusion = Inclusion(args.inclusion_relationship)
                    annot.to_mask(wsi_height, wsi_width, inclusion)
                else:
                    annot.to_mask(wsi_height, wsi_width)
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               annot, args.one_shot, args.patch_without_annotation,
                               args.only_foreground, args.patch_on_annotated,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)
            else:
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               args.only_foreground,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)

        elif args.method == "segmentation":

            if args.annotation:
                annot = Annotation(args.annotation)

                if args.inclusion_relationship:
                    inclusion = Inclusion(args.inclusion_relationship)
                    annot.to_mask(wsi_height, wsi_width, inclusion)
                else:
                    annot.to_mask(wsi_height, wsi_width)
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               annot, args.patch_without_annotation,
                               args.only_foreground, args.patch_on_annotated,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)

            else:
                slide.to_patch(args.method, args.patch_width, args.overlap_width,
                               args.only_foreground,
                               args.start_sample, args.finished_sample,
                               args.extract_patches, args.magnification)
