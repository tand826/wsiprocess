class Inclusion:

    def __init__(self, path):
        with open(self.path, "r") as f:
            self.inclusion_file = f.readlines()
        self.readinclusion()

    def read_inclusion(self):
        # One line like -> {"malignant", ["benign", "stroma", "vessel"]}
        # becomes {"malignant", ["benign", "stroma", "vessel"]} of python dict.
        # It means the mask excludes "benign, stroma, vessel from malignant".
        self.inclusion = {}
        for line in self.inclusion_file:
            line_ = line.strip().split(" ")
            base, exclude = line_[0], line[1:]
            setattr(self, base, exclude)
