"""Module for constructing argparse-manpage CLI command."""

import sys
from argparse import ArgumentParser
from collections import defaultdict
from functools import cached_property, reduce
from os import _exit as exit
from subprocess import run as sys_run

from argparse_manpage.cli import ap as base_parser
from more_itertools import always_iterable, first, flatten

from tools.config import Config

bp = breakpoint


class Command():
    """Class for constructing argparse-manpage command."""

    program = "argparse-manpage"

    """Used to store Config object"""
    cfg = None

    """Used to store command line options"""
    options: dict

    """Mapping of argparse.dest to argparse.name"""
    _option_flags: dict = {}

    _parser: ArgumentParser = None

    def __init__(self, outdir="share/man/man1", **kwargs):
        """Initialize argparse parser.

        Keyword Arguments
        -----------------
        * config (Config): Config object
        * outdir (str): output dir
        * kwargs: options to add

        """
        # initialize Config object
        self.cfg = kwargs.pop("config", Config())

        self.outdir = outdir

        # add all kwargs to self.options
        self.options = defaultdict(set)
        for key, value in kwargs.items():
            self.add(key, value)

        outfile = f"{self.cfg.name}.1"
        if self.outdir:
            outfile = f"{self.outdir}/{outfile}"
        self.add("output", outfile, override=False)

    def add(self, name, value, override=True):
        """Add option.

        Arguments
        ---------
        * name (str)         : option name
        * value (str)        : option value
        * override (bool)    : override if option already exists
                               (default: True)
        """
        if not value:
            return

        name = name.replace("_", "-")
        if (not override) and (name in self.options):
            return

        values = always_iterable(value)
        for value in values:
            self.options[name].add(value)

    @cached_property
    def values(self):
        """Return the parsed args from the ArgumentParser."""
        values = self.parser.parse_args(self.output_args + sys.argv[1:])
        return values

    def parse(self):
        """Add results of argparse.parse to self.options."""
        values = vars(self.values)
        for attr, value in values.items():
            # strip internal options
            if attr not in self.option_flags:
                continue
            name = self.option_flags[attr]
            self.add(name, value)

    @property
    def command(self):
        """Return list of strings to run at the command line."""
        return [self.program, *self.output_args]

    @property
    def output_args(self):
        """List of --key [value] style arguments for the command line."""
        #  options = [(f"--{k}", v) for k,v in self.options.items()]
        func = lambda prev, kvp: prev + \
            [(f"--{kvp[0]}", value) for value in kvp[1]]
        options = reduce(func, self.options.items(), [])
        opts = list(flatten(options))
        return opts

    def argparse_manpage_parser(self) -> ArgumentParser:
        """Return the parser for the argparse-manpage CLI options."""
        return base_parser

    @cached_property
    def parser(self) -> ArgumentParser:
        """Return ArgumentParser."""
        # argparse_manpage parser
        base_parser.add_help = False

        self._parser = ArgumentParser(
            description="Generate man page.",
            parents=[base_parser],
            conflict_handler="resolve",
        )

        # help group that contains the main parser options
        # which is all of the base_parser options
        # in other words, the argparse-manpage CLI options
        parent_group = first(sorted(
            self._parser._action_groups,
            key=lambda x: len(x._group_actions),
            reverse=True
        ))
        parent_group.title = "argparse-manpage options"
        help_arg = parent_group._group_actions.pop(0)
        self.parent_group = parent_group

        # help group that contains the mkman specific options
        mkman_group = self._parser.add_argument_group("mkman options")
        mkman_group._group_actions.insert(0, help_arg)
        mkman_group.add_argument(
            "-d",
            "--outdir",
            help="directory of output file"
        )
        mkman_group.add_argument(
            "-V",
            "--verbose",
            action="store_true",
            help="print git command"
        )
        self.mkman_group = mkman_group

        return self._parser

    @cached_property
    def option_flags(self) -> dict:
        """Return mapping of attr name -> option name.

        From the argparse-manpage parser.
        """
        for action in self.parent_group._group_actions:
            options = sorted(action.option_strings, key=len, reverse=True)

            attr = action.dest
            option = first(options).lstrip("-")

            if attr in self._option_flags:
                continue

            self._option_flags[attr] = option

        return self._option_flags

    def __str__(self):
        """Command that can be pasted on the command line."""
        return " ".join(self.command)

    def run(self):
        """Execute on the shell via subprocess.run."""
        result = sys_run(self.command)
        if result.returncode:
            exit(result.returncode)
        return result
