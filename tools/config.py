"""."""

from copy import deepcopy
from pathlib import Path

from poetry.core.pyproject.toml import PyProjectTOML
from more_itertools import first_true

from tools import abort

class Config():
    """Class for poetry config"""
    ROOTDIR = Path(__file__).parent.parent
    _poetry = None
    _url = None

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

        if not self.toml.is_poetry_project():
            abort(f"Not a poetry project: {self.ROOTDIR}")

    @property
    def urls(self):
        """List of all possible urls"""
        return [self.poetry.get(key) for key in ("homepage", "repository", "documentation")]

    @property
    def url(self):
        """Return the first stored url or first not null url"""
        if self._url:
            return self._url

        return first_true(self.urls)

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

