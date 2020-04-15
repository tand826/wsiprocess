# -*- coding: utf-8 -*-
"""Object to define rules for extracting patches.

Rule file should be a json file.
The content of rule.json is like below.

Example:
    Json data below defines

    - extract the patches of benign and malignant
    - benign includes stroma but excludes malignant or uncertain
    - malignant means malignant itself but excludes benign

    ::

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
                    "benign"
                ]
            }
        }
"""

import json


class Rule:
    """Base class for rule.

    Args:
        path (str): Path to the rule.json file.

    Attributes:
        classes (list): List of the classes. i.e. ["benign", "malignant"]
        read_rule (dict): Dict of rules.
            i.e. {"benign": {"inclues": ["stroma"]}}
    """

    def __init__(self, path):
        self.classes = []
        with open(path, "r") as f:
            self.rule_file = json.load(f)
        self.read_rule()

    def read_rule(self):
        """Read the rule file.

        Parse the rule file and save as the classes.
        """
        self.rule = {}
        for base, incl_excl in self.rule_file.items():
            setattr(self, base, incl_excl)
            self.classes.append(base)
