import json


class Rule:
    """
    Rule file should be a json file.
    The content is like below.
    This file defines
        - extract the patches of benign and malignant
        - benign includes stroma but excludes malignant or uncertain
        - malignant means malignant itself but excludes benign
    {
        "benign" : {
            "includes" : [
                "stroma"
            ],
            "excludes : [
                "malignant",
                "uncertain"
            ]
        },
        "malignant": {
            "includes" : [
            ],
            "excludes" :[
                "benign"  # This line does not exclude stroma from malignant
            ]
        }
    }
    """

    def __init__(self, path):
        self.classes = []
        with open(path, "r") as f:
            self.rule_file = json.load(f)
        self.read_rule()

    def read_rule(self):
        self.rule = {}
        for base, incl_excl in self.rule_file.items():
            setattr(self, base, incl_excl)
            self.classes.append(base)
