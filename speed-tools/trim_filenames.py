import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

from tqdm import tqdm

PROG_NAME = 'tfn'


def setup_parser(parser: ArgumentParser) -> None:
    """
    Set up an argument parser according to the specifications of the 'trim filenames' sub-command.

    :param parser: The parser to be modified.
    """
    parser.description = ('Remove the prefix and/or postfix of all files that have them in the indicated directories. '
                          'File extensions are ignored.')
    parser.add_argument(
        '-d', '--directory',
        dest='directories',
        required=True,
        nargs='+',
        type=str,
        metavar='DIR',
        help='specify a directory in which filenames are trimmed'
    )
    parser.add_argument(
        '-b', '--prefix',
        dest='prefixes',
        nargs='+',
        type=str,
        default=[],
        metavar='PREFIX',
        help='specify a prefix to be trimmed from filenames'
    )
    parser.add_argument(
        '-e', '--postfix',
        dest='postfixes',
        nargs='+',
        type=str,
        default=[],
        metavar='POSTFIX',
        help='specify a postfix to be trimmed from filenames'
    )
    parser.set_defaults(func=trim_filenames)


def trim_filenames(directories: list[str], prefixes: list[str], postfixes: list[str], **_kwargs) -> None:
    """
    Remove the prefix and/or postfix of all files that have them in the indicated directories.
    File extensions are ignored.

    :param directories: The list of directories in which filenames are trimmed.
    :param prefixes: The list of prefixes to be trimmed.
    :param postfixes: The list of postfixes to be trimmed.
    :param _kwargs: Ignored.
    """
    if len(prefixes) == 0 and len(postfixes) == 0:
        print('Error: At least one prefix or one postfix must me specified', file=sys.stderr)
        exit(1)

    errors: list[str] = []
    for dir_str in directories:
        dir_path = Path(dir_str)
        if not dir_path.exists():
            errors.append(f'Path "{dir_path}" does not exist.')
            continue
        if not dir_path.is_dir():
            errors.append(f'Path "{dir_path}" is not a directory.')
            continue

    if 0 < len(errors):
        print('Error: Incorrect directories provided:', file=sys.stderr)
        for e in errors:
            print(f'\t{e}', file=sys.stderr)
        exit(1)

    if 0 < len(prefixes):
        prefix_pattern = re.compile(rf'^(?:{"|".join(prefixes)})*')
    else:
        prefix_pattern = None

    if 0 < len(postfixes):
        postfix_pattern = re.compile(rf'(?:{"|".join(postfixes)})*$')
    else:
        postfix_pattern = None

    for dir_str in directories:
        dir_path = Path(dir_str)
        files: list[tuple[str, str, str]] = []
        for fullname in os.listdir(dir_path):
            sub_path = dir_path / fullname
            if not sub_path.is_file():
                # Skip directories
                continue

            idx = fullname.find('.')
            if idx == -1:
                idx = len(fullname)
            name, extension = fullname[:idx], fullname[idx:]
            if len(name) == 0:
                # Skip dot files
                continue

            old_len = len(name)
            if prefix_pattern:
                match = prefix_pattern.search(name)
                if match and 0 < len(match.group()):
                    name = name[len(match.group()):]
            if postfix_pattern:
                match = postfix_pattern.search(name)
                if match and 0 < len(match.group()):
                    name = name[:len(match.group()) - 1]

            if len(name) != old_len:
                files.append((fullname, name, extension))

        for file in tqdm(files):
            filepath = dir_path / (file[1] + file[2])
            counter = 0
            while filepath.exists():
                filepath = dir_path / (file[1] + f'({counter})' + file[2])
                counter += 1

            os.rename(dir_path / file[0], filepath)
