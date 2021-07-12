"""."""

from copy import deepcopy
from pathlib import Path
import re

from poetry.core.pyproject.toml import PyProjectTOML
from more_itertools import first_true, first

from tools import abort

class Config():
    """Class for poetry config"""
    ROOTDIR = Path(__file__).parent.parent
    _poetry = None
    _url = None

    """Author parsing pattern"""
    author_regex: re.Pattern = re.compile(r'(?P<name>.+) <(?P<email>.+)>')

    """Used to store tool.poetry section of pyproject.toml """
    poetry = {}

    """Used to store tool.poetry.dependencies section of pyproject.toml """
    dependencies = {}

    """Used to store tool.poetry.dev_dependencies section of pyproject.toml """
    dev_dependencies = {}

    """Used to store tool.build-system section of pyproject.toml """
    build_system = {}

    def __init__(self):
        """Load pyproject.toml"""
        self.toml = PyProjectTOML( self.ROOTDIR / "pyproject.toml")
        self.poetry = self.get("tool", "poetry", default={})
        self.dependencies = self.get("tool", "poetry", "dependencies", default={})
        self.dev_dependencies = self.get("tool", "poetry", "dev-dependencies",
                                         default={})
        self.build_system = self.get("tool", "poetry", "build-system", default={})
        self.python = self.get("tool", "poetry", "dependencies", "python", default=None)

        if not self.toml.is_poetry_project():
            abort(f"Not a poetry project: {self.ROOTDIR}")

    @property
    def urls(self):
        """List of all possible urls"""
        return [self.poetry.get(key) for key in ("homepage", "repository", "documentation")]

    @property
    def url(self):
        """Return the first stored url or first not null url"""
        if not self._url:
            self._url = first_true(self.urls)

        return self._url

    @property
    def author(self):
        """Return the first string in tool.poetry.authors"""
        return first(self.get("tool", "poetry", "authors", default=[]), default="")

    @property
    def author_email(self):
        """Return author email parsed from tool.poetry.authors"""
        if not self.author:
            return

        match = self.author_regex.search(self.author)
        if match:
            return match.group("email")
        else:
            return " "

    @property
    def author_name(self):
        """Return author name parsed from tool.poetry.authors"""
        if not self.author:
            return

        match = self.author_regex.search(self.author)
        if match:
            return match.group("name")
        else:
            return self.author

    def __getattr__(self, attr):
        """Enable object.name access for attributes in tool.poetry section"""
        try:
            return self.__dict__["poetry"][attr]
        except KeyError:
            return self.__getattribute__(attr)

    def get(self, *keys, data=NotImplemented, default=None):
        """Return value from config

        Arguments
        ---------
        * *keys             : list of keys
        * default (optional): default to return if no value
        * data              : used internally for recursion

        Example
        -------
        >>> cfg = Config()
        >>> cfg.get("tool", "poetry", "license")
        MIT
        >>> cfg.get("tool", "poetry", "readme", default="README.md")
        README.md
        >>> cfg.get("tool", "poetry", "readme")
        """

        if data is NotImplemented:
            data = deepcopy(self.toml.data)

        keys = list(keys)
        key = keys.pop(0)

        if not isinstance(data, dict):
            abort(f"not a dict: {data}")

        if keys:
            return self.get(*keys, data=data.get(key, {}), default=default)
        else:
            return data.get(key, default)

