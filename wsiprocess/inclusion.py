class Inclusion:

    def __init__(self, path):
        with open(path, "r") as f:
            self.inclusion_file = f.readlines()
        self.read_inclusion()

    def read_inclusion(self):
        # A line in file like -> {"malignant", ["benign", "stroma", "vessel"]}
        # becomes {"malignant", ["benign", "stroma", "vessel"]} of python dict.
        # It means the mask excludes "benign, stroma, vessel from malignant".
        self.inclusion = {}
        for line in self.inclusion_file:
            line_ = [i.strip() for i in line.split(" ")]
            base, exclude = line_[0], line_[1:]
            setattr(self, base, exclude)
