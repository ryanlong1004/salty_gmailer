"""Rule abstraction class"""
from collections import defaultdict
from typing import Any
from pathlib import Path

import yaml


class Rule(defaultdict):
    """Rule abstraction for defining rules

    Args:
        defaultdict (dict): yaml data as python dict
        mailer (Mailer): performs the actual operations
    """

    def __init__(self, data, mailer):
        super().__init__(**data)
        self.mailer = mailer

    def __getattr__(self, __key: Any) -> Any:
        return super().get(__key, [])

    def __call__(self):
        """modify_labels add or remove labels from filteres messages"""
        self.mailer.modify_labels(self.messages, self.remove_labels, self.add_labels)

    @property
    def messages(self):
        """messages returns messages filterd on search criteria

        Returns:
            _type_: _description_
        """
        search_terms = []
        for term in self.search:
            search_terms.extend([f"{k}:{v}" for (k, v) in term.items()])
        return self.mailer.search(search_terms)

    @classmethod
    def from_path(cls, path: Path, mailer) -> "Rule":
        """creates instance of Rule from a yaml file"""
        with open(path, "r", encoding="utf-8") as _file:
            return cls(yaml.safe_load(_file), mailer)
