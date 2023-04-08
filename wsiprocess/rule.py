# -*- coding: utf-8 -*-
"""Object to define rules for extracting patches.
Rule file should be a json file or a dict. The content of rule.json is like
below.

Example:
    Json data below defines

    - extract the patches of benign and malignant
    - benign includes stroma but excludes malignant or uncertain
    - malignant means malignant itself but excludes benign

    .. code-block:: python

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

from pathlib import Path
import json


class Rule:
    """Base class for rule.

    Args:
        rule(str or dict): Path to the rule.json or the rule dict.

    Attributes:
        classes (list): List of the classes. i.e. ["benign", "malignant"]
    """

    def __init__(self, rule):
        self.classes = []
        if isinstance(rule, (str, Path)):
            with open(rule, "r") as f:
                base_rule = json.load(f)

        elif isinstance(rule, dict):
            base_rule = rule

        else:
            raise NotImplementedError(
                f"rule must be str or dist, but got {type(rule)}")

        self.load_rule(base_rule)

    def load_rule(self, rule: dict):
        """Read the rule file.

        Parse the rule file and save as the classes.
        """
        for base, incl_excl in rule.items():
            self.assert_incl_excl(incl_excl)
            setattr(self, base, incl_excl)
            self.classes.append(base)

    def assert_incl_excl(self, incl_excl: dict):
        """Assert the rule has assumed keys.

        Supposed shape is like below

        {"includes": ["stroma"], "excludes": ["malignant", "uncertain"]}

        """
        assert isinstance(incl_excl, dict), "each object must be dict"
        msg = "each dict must have {}"
        assert "includes" in incl_excl.keys(), msg.format("includes")
        assert "excludes" in incl_excl.keys(), msg.format("excludes")

    def __getitem__(self, class_name):
        return getattr(self, class_name)
