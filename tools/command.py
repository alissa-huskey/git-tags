import argparse
from subprocess import run
import sys
from os import _exit as exit

from more_itertools import first, flatten
from build_manpages.cli import ap as base_parser

from tools.config import Config

class Command():
    """Class for constructing argparse-manpage command"""

    program = "argparse-manpage"

    """Used to store Config object"""
    cfg = None

    """Used to store command line options"""
    options: dict

    """Mapping of argparse.dest to argparse.name"""
    option_names: dict

    def __init__(self, outdir="share/man/man1", **kwargs):
        """Initialize argparse parser

        Keyword Arguments
        -----------------
        * config (Config): Config object
        * outdir (str): output dir
        * kwargs: options to add

        """

        # initialize Config object
        self.cfg = kwargs.pop("config", Config())

        self.outdir = outdir

        # initialize option_names dict
        self.option_names = {}

        # initialize Argument Parser
        base_parser.add_help = False
        self.parser = argparse.ArgumentParser(
            description="Generate man page.",
            parents=[base_parser],
            conflict_handler="resolve",
        )
        default_group = first(sorted(
            self.parser._action_groups,
            key=lambda x: len(x._group_actions),
            reverse=True
        ))
        default_group.title = "argparse-manpage options"

        # remove help from argparse-manpage group
        help_arg = default_group._group_actions.pop(0)

        internal = self.parser.add_argument_group("mkman options")
        internal._group_actions.insert(0, help_arg)
        internal.add_argument(
            "-d",
            "--outdir",
            help="directory of output file"
        )
        internal.add_argument(
            "-V",
            "--verbose",
            action="store_true",
            help="print git command"
        )

        # add all kwargs to self.options
        self.options = {}
        for key, value in kwargs.items():
            self.add(key, value)

        # generate option_names mapping for use in self.parse()
        for action in self.parser._actions:
            names = sorted(action.option_strings, key=len, reverse=True)
            if action in internal._group_actions:
                continue
            self.option_names[action.dest] = first(names).lstrip("-")

        outfile = f"{self.cfg.name}.1"
        if self.outdir:
            outfile = f"{self.outdir}/{outfile}"
        self.add("output", outfile, override=False)

    def add(self, name, value, override=True):
        """Add option

        Arguments
        ---------
        * name (str)         : option name
        * value (str)        : option value
        * override (bool)    : override if option already exists (default: True)
        """
        if not value:
            return

        if (not override) and (name in self.options):
            return

        self.options[name.replace("_", "-")] = value

    def parse(self):
        """Add results of argparse.parse() to self.options"""
        self.values = self.parser.parse_args(self.args + sys.argv[1:])
        for name, value in vars(self.values).items():
            # strip internal options
            if name not in self.option_names:
                continue
            self.add(self.option_names[name], value)
        return self.values

    @property
    def command(self):
        """List containing command and arguments to be passed to subprocess.run"""
        return [self.program] + self.args

    @property
    def args(self):
        """List of --key [value] style arguments for the command line"""
        opts = [ (f"--{k}", v) for k,v in self.options.items() ]
        return list(flatten(opts))

    def __str__(self):
        """Command that can be pasted on the command line"""
        return " ".join(self.command)

    def run(self):
        """Execute on the shell via subprocess.run"""
        result = run(self.command)
        if result.returncode:
            exit(result.returncode)
        return result
