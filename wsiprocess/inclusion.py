class Inclusion:

    def __init__(self, path):
        with open(self.path, "r") as f:
            self.clsfile = f.readlines()
        self.readinclusion()

    def read_inclusion(self):
        # {"malignant", ["benign", "stroma", "vessel"]}
        self.inclusion = {}
        for line in self.clsfile:
            line_ = line.strip().split(" ")
            base, exclude = line_[0], line[1:]
            setattr(self, base, exclude)
