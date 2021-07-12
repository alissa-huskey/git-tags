import subprocess
import argparse
from sys import stderr

__version__ = "0.1.0"

def shell(*cmd):
    """Run the command in text mode and capture output, return CompletedProcess instance
    raise CalledProcessError for non-zero exit code
    """
    result = subprocess.run(cmd, text=True, capture_output=True)
    result.check_returncode()
    return result

def color(name, default="normal"):
    """Return git config value for color.name or default"""
    result = shell("git", "config", f"color.{name}")
    value = result.stdout.strip() or default
    return f"%(color:{value})"

def gettags():
    """Return the length of the longest tag"""
    result = shell("git", "tag")
    return result.stdout.splitlines()

def execute(is_verbose, options):
    """Construct and execute git command to print list of tags including: tag, sha, date, annotation/message"""
    tags = gettags()
    if not tags:
        return

    # length of longest tag
    width = max(map(len, tags))

    # construct format string
    fmt = (
        color("decorate.tag") + f"%(align:{width},left)%(refname:short)%(end) "  + # tag
        color("diff.meta") + "%(objectname:short)%(color:reset) "                  # SHA
        "%(authordate:short)%(*authordate:short) "                                 # date
        "%(subject)"                                                               # annotation/message
    )

    # construct command
    command=[
        "git",
        "for-each-ref",
        "--sort=-taggerdate",
        f"--format={fmt}",
        *options,
        "refs/tags"
    ]

    if is_verbose:
        print(">", *command, "\n", file=stderr)

    # run command
    subprocess.run(command)

def parser():
    """Return ArgumentParser object. Used by argparse-manpage and cli()"""
    parser = argparse.ArgumentParser(
        prog="git-tags",
        description="A git extension to print a detailed list of tags.",
        epilog="Remaining options are forwarded to git. See: git help for-each-ref"
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
    """Parse arguments and execute git command"""
    args, options = parser().parse_known_args()

    if args.format:
        parser.error(f"argument unrecognized argument: --format")

    execute(args.verbose, options)

if __name__ == "__main__":
    cli()
