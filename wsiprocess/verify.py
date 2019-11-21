
def verify_outdir(args):
    base_dir = args.output_dir/args.wsi
    verify_dir(base_dir)
    if args.method == "segmentation":
        verify_dir(base_dir/"masks")
    if args.start_sample:
        verify_dir(base_dir/"start_sample")
    if args.finished_sample:
        verify_dir(base_dir/"finished_sample")
    if args.extract_patches:
        verify_dir(base_dir/"patches")


def verify_dir(path):
    if not path.exists():
        path.mkdir(parents=True)


def verify_magnification(slide, magnification):
    basemsg = "Magnification for this slide has to be smaller than"
    msg = "{} {}".format(basemsg, slide.slide.magnification)
    assert slide.slide.magnification < magnification, msg
