from argparse import ArgumentParser

from . import PACKAGE, VERSION, DESCRIPTION, REPOSITORY
from . import trim_filenames

parser = ArgumentParser(prog=PACKAGE, description=DESCRIPTION, epilog=f'%(prog)s {VERSION} source at: {REPOSITORY}')
parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
subparsers = parser.add_subparsers(required=True)

# Setup sub-commands
trim_filenames.setup_parser(subparsers.add_parser(trim_filenames.PROG_NAME))


def main() -> None:
    """
    Main function.
    """
    args = parser.parse_args()
    args.func(**args.__dict__)
