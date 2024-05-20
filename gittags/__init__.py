"""git-tags module."""

import argparse
from functools import cached_property
from sys import stderr

from git import Git, Repo
from more_itertools import flatten

bp = breakpoint

__version__ = "0.1.0"


class GitTags():
    """Construct the detailed git-tags output."""

    def __init__(self, is_verbose, git_args):
        """Create the object."""
        self.is_verbose = is_verbose
        self.git_args = git_args

    @cached_property
    def git(self) -> Git:
        """Return a Git object."""
        return Git()

    def color(self, field):
        """Return the color for a git field."""
        color = self.git.config(f"color.{field}")
        return f"%(color:{color})"

    @cached_property
    def repo(self) -> Repo:
        """Return a Repo object."""
        return Repo()

    @property
    def tags(self) -> list[str]:
        """Return a list of tag names."""
        return [t.name for t in self.repo.tags]

    @property
    def width(self):
        """Return the length of the longest tag."""
        return max(map(len, self.tags))

    @property
    def format(self):
        """Return the format string."""
        fmt = {
            "tag": (
                self.color("decorate.tag"),
                f"%(align:{self.width},left)%(refname:short)%(end) ",
            ),
            "SHA": (
                self.color("diff.meta"),
                "%(objectname:short)%(color:reset) ",
            ),
            "date": ("%(authordate:short)%(*authordate:short) ",),
            "subject": ("%(subject)"),
        }

        text = "".join(flatten(fmt.values()))
        return text

    @property
    def args(self):
        """Return the CLI command to run."""
        args = [
            "--sort=-taggerdate",
            f"--format={self.format}",
            *self.git_args,
            "refs/tags"
        ]
        return args

    def display(self):
        """Run the git command."""
        if self.is_verbose:
            print(
                "git",
                "for-each-ref",
                *[repr(a) for a in self.args],
                "\n",
                file=stderr
            )

        output = self.git.for_each_ref(*self.args, "--color=always")
        print(output)


def parser():
    """Return ArgumentParser object.

    Used by argparse-manpage and cli().
    """
    parser = argparse.ArgumentParser(
        prog="git-tags",
        description="A git extension to print a detailed list of tags.",
        epilog=(
            "Remaining options are forwarded to git. "
            "See: git help for-each-ref"
        )
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # --format flag and optional value
    parser.add_argument(
        "--format",
        help=argparse.SUPPRESS,
        default=False,
        const=True,
        nargs="?",
    )

    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help="print git command"
    )

    return parser


def cli():
    """Parse arguments and execute git command."""
    args, options = parser().parse_known_args()

    if args.format:
        parser.error("argument unrecognized argument: --format")

    tags = GitTags(args.verbose, options)
    tags.display()


if __name__ == "__main__":
    cli()
